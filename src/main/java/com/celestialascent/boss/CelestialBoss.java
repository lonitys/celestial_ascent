package com.celestialascent.boss;

import com.celestialascent.core.ModConfig;
import com.celestialascent.progress.Constellations;
import com.celestialascent.progress.Progress;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Base class for every Celestial Ascent boss: boss bar, phases, multiplayer health scaling,
 * per-player loot, progression recording and anti-cheese rules. Subclasses declare attacks.
 *
 * Animation contract (GeckoLib): "idle", "walk" (or {@link #moveAnimation()}), "death",
 * "phase" and "attack.&lt;attackId&gt;" for every animated attack.
 */
public abstract class CelestialBoss extends Monster implements GeoEntity {
    private static final EntityDataAccessor<Integer> PHASE = SynchedEntityData.defineId(CelestialBoss.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> ATTACKING = SynchedEntityData.defineId(CelestialBoss.class, EntityDataSerializers.BOOLEAN);
    public static final int DEATH_TICKS = 60;
    public static final int PHASE_TICKS = 40;

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private final ServerBossEvent bossEvent;
    private final Map<UUID, Float> damageBy = new HashMap<>();
    protected final List<BossAttack> attacks = new ArrayList<>();
    private final Map<String, Integer> cooldowns = new HashMap<>();

    private BossAttack current;
    private int attackTick;
    private int transitionTicks;
    private int globalCooldown = 40;
    private int unreachableTicks;
    private boolean scaledOnce;
    private BlockPos home;

    protected CelestialBoss(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.bossEvent = new ServerBossEvent(getDisplayName(), barColor(), BossEvent.BossBarOverlay.NOTCHED_10);
        this.bossEvent.setDarkenScreen(false);
        this.xpReward = 500;
        registerAttacks();
    }

    // ---- subclass contract -------------------------------------------------------------

    /** Progression id, e.g. celestialascent:frost_titan. */
    public abstract ResourceLocation bossId();

    /** Base max health before config and player scaling. */
    public abstract double baseMaxHealth();

    /** Health fractions at which the next phase starts, descending (e.g. {0.5f}). */
    protected abstract float[] phaseThresholds();

    protected abstract BossEvent.BossBarColor barColor();

    /** Fill {@link #attacks}. Called from the constructor; lambdas run later. */
    protected abstract void registerAttacks();

    protected void onPhaseChange(int newPhase) {}

    /** Called every server tick outside phase transitions (auras, ambient hazards). Target may be null. */
    protected void passiveTick(LivingEntity target) {}

    /** Players within radius (alive, not spectating). */
    public List<Player> playersNear(double radius) {
        return level().getEntitiesOfClass(Player.class, getBoundingBox().inflate(radius),
                p -> p.isAlive() && !p.isSpectator() && !p.isCreative());
    }

    /** Ground position (top of the first solid block at or below y+3). */
    public Vec3 ground(double x, double z, double fromY) {
        BlockPos.MutableBlockPos m = BlockPos.containing(x, fromY + 3, z).mutable();
        for (int i = 0; i < 16 && !level().getBlockState(m.below()).isSolid(); i++) m.move(0, -1, 0);
        return new Vec3(x, m.getY(), z);
    }

    /** Position of an attack origin in front of the boss at a height fraction of its body. */
    public Vec3 front(double forward, double heightFraction) {
        Vec3 look = Vec3.directionFromRotation(0, getYRot());
        return position().add(look.scale(forward)).add(0, getBbHeight() * heightFraction, 0);
    }

    /** Ambient particles shown around the boss on the client. */
    protected ParticleOptions ambientParticle() { return null; }

    protected String moveAnimation() { return "walk"; }

    /** Flying bosses skip the "pillar up" anti-cheese teleport. */
    protected boolean canFlyToTarget() { return false; }

    // ---- static helpers (unit-tested) --------------------------------------------------

    /** Max health for n players within range: base * (1 + perPlayer * (n - 1)). */
    public static double scaledHealth(double base, int players, double perPlayer) {
        return base * (1.0 + perPlayer * Math.max(0, players - 1));
    }

    /** Phase index for a health fraction: number of thresholds at or above the fraction. */
    public static int phaseFor(float fraction, float[] thresholds) {
        int p = 0;
        for (float t : thresholds) if (fraction <= t) p++;
        return p;
    }

    // ---- setup ---------------------------------------------------------------------------

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder b) {
        super.defineSynchedData(b);
        b.define(PHASE, 0);
        b.define(ATTACKING, false);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new BossChaseGoal(this));
        goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 32f));
        goalSelector.addGoal(9, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    public int phase() { return entityData.get(PHASE); }
    public boolean isAttacking() { return entityData.get(ATTACKING); }
    public boolean inTransition() { return transitionTicks > 0; }
    public BossAttack currentAttack() { return current; }

    public void setHome(BlockPos pos) { this.home = pos; }

    // ---- ticking ---------------------------------------------------------------------------

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) {
            ParticleOptions p = ambientParticle();
            if (p != null && random.nextInt(2) == 0) {
                level().addParticle(p, getRandomX(1.2), getRandomY(), getRandomZ(1.2), 0, 0.02, 0);
            }
        }
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (!scaledOnce || tickCount % 100 == 0) updateScaling();
        bossEvent.setProgress(getHealth() / getMaxHealth());

        int newPhase = phaseFor(getHealth() / getMaxHealth(), phaseThresholds());
        if (newPhase > phase()) beginPhase(newPhase);

        if (transitionTicks > 0) {
            transitionTicks--;
            getNavigation().stop();
            return;
        }
        cooldowns.replaceAll((k, v) -> Math.max(0, v - 1));
        LivingEntity target = getTarget();
        if (target != null && !target.isAlive()) target = null;
        passiveTick(target);

        if (current != null) {
            if (target == null) {
                endAttack(null);
            } else {
                if (current.locksMovement) getNavigation().stop();
                getLookControl().setLookAt(target, 30f, 30f);
                current.onTick.run(this, target, attackTick);
                attackTick++;
                if (attackTick >= current.duration) endAttack(target);
            }
        } else if (target != null) {
            if (globalCooldown > 0) globalCooldown--;
            else pickAttack(target);
        }
        antiCheese(target);
    }

    private void pickAttack(LivingEntity target) {
        int total = 0;
        List<BossAttack> options = new ArrayList<>();
        for (BossAttack a : attacks) {
            if (cooldowns.getOrDefault(a.id, 0) == 0 && a.usable(this, target, phase())) {
                options.add(a);
                total += a.weight;
            }
        }
        if (options.isEmpty()) return;
        int roll = random.nextInt(total);
        for (BossAttack a : options) {
            roll -= a.weight;
            if (roll < 0) {
                startAttack(a, target);
                return;
            }
        }
    }

    private void startAttack(BossAttack a, LivingEntity target) {
        current = a;
        attackTick = 0;
        entityData.set(ATTACKING, true);
        if (a.animated) triggerAnim("attack", a.id);
        a.onStart.run(this, target, 0);
    }

    private void endAttack(LivingEntity target) {
        if (current == null) return;
        if (target != null) current.onEnd.run(this, target, attackTick);
        cooldowns.put(current.id, current.cooldown);
        current = null;
        entityData.set(ATTACKING, false);
        globalCooldown = phase() >= 2 ? 6 : phase() == 1 ? 12 : 20;
    }

    private void beginPhase(int newPhase) {
        entityData.set(PHASE, newPhase);
        if (current != null) endAttack(getTarget());
        transitionTicks = PHASE_TICKS;
        triggerAnim("attack", "phase");
        playSound(SoundEvents.WITHER_SPAWN, 2.0f, 0.6f + 0.1f * newPhase);
        if (level() instanceof ServerLevel sl) {
            sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, getX(), getY() + getBbHeight() / 2, getZ(), 2, 0.5, 0.5, 0.5, 0);
        }
        onPhaseChange(newPhase);
    }

    private void updateScaling() {
        scaledOnce = true;
        int players = Math.max(1, level().getEntitiesOfClass(Player.class, getBoundingBox().inflate(64),
                p -> !p.isSpectator() && p.isAlive()).size());
        double max = scaledHealth(baseMaxHealth() * ModConfig.BOSS_HEALTH_MULT.get(), players, ModConfig.BOSS_SCALE_PER_PLAYER.get());
        AttributeInstance inst = getAttribute(Attributes.MAX_HEALTH);
        if (inst != null && Math.abs(inst.getBaseValue() - max) > 0.5) {
            float fraction = getHealth() / getMaxHealth();
            inst.setBaseValue(max);
            setHealth((float) (fraction * max));
        }
    }

    private void antiCheese(LivingEntity target) {
        if (home != null && distanceToSqr(Vec3.atCenterOf(home)) > 48 * 48) {
            teleportTo(home.getX() + 0.5, home.getY() + 1, home.getZ() + 0.5);
            setTarget(null);
            return;
        }
        if (target == null || canFlyToTarget()) {
            unreachableTicks = 0;
            return;
        }
        boolean stuck = getNavigation().isDone() && distanceTo(target) > 6;
        boolean above = target.getY() - getY() > 4 && horizontalDistance(target) < 8;
        unreachableTicks = (stuck || above) ? unreachableTicks + 1 : 0;
        if (unreachableTicks > 160) {
            unreachableTicks = 0;
            Vec3 p = target.position().add((random.nextDouble() - 0.5) * 4, 0, (random.nextDouble() - 0.5) * 4);
            if (level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.REVERSE_PORTAL, getX(), getY() + 1, getZ(), 40, 0.6, 1, 0.6, 0.05);
            }
            teleportTo(p.x, target.getY(), p.z);
            playSound(SoundEvents.ENDERMAN_TELEPORT, 2f, 0.6f);
        }
    }

    public double horizontalDistance(Entity e) {
        double dx = e.getX() - getX(), dz = e.getZ() - getZ();
        return Math.sqrt(dx * dx + dz * dz);
    }

    // ---- damage --------------------------------------------------------------------------

    @Override
    public boolean isInvulnerableTo(DamageSource src) {
        if (src.is(DamageTypes.IN_WALL) || src.is(DamageTypes.DROWN) || src.is(DamageTypes.FALL)
                || src.is(DamageTypes.CACTUS) || src.is(DamageTypes.SWEET_BERRY_BUSH) || src.is(DamageTypes.CRAMMING)
                || src.is(DamageTypes.FLY_INTO_WALL)) {
            return true;
        }
        return super.isInvulnerableTo(src);
    }

    @Override
    public boolean hurt(DamageSource src, float amount) {
        boolean bypass = src.is(DamageTypeTags.BYPASSES_INVULNERABILITY);
        if (!bypass) {
            if (transitionTicks > 0 || isDeadOrDying()) return false;
            // A single hit can never take more than 8% of max health (one-shot weapons, exploits).
            amount = Math.min(amount, getMaxHealth() * 0.08f);
        }
        float before = getHealth();
        boolean hit = super.hurt(src, amount);
        if (hit && !level().isClientSide) {
            Entity attacker = src.getEntity();
            if (attacker instanceof Player p) {
                damageBy.merge(p.getUUID(), Math.max(0, before - getHealth()), Float::sum);
            }
        }
        return hit;
    }

    /** Applies scaled boss damage to everything (except bosses) within radius of center. */
    public void hitArea(Vec3 center, double radius, float damage, double knockback) {
        AABB box = new AABB(center, center).inflate(radius);
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, box, e -> e != this && !(e instanceof CelestialBoss) && e.isAlive())) {
            if (e.position().distanceTo(center) > radius + e.getBbWidth()) continue;
            hitTarget(e, damage);
            if (knockback > 0) {
                Vec3 push = e.position().subtract(center).normalize().scale(knockback);
                e.push(push.x, 0.35 * knockback, push.z);
                e.hurtMarked = true;
            }
        }
    }

    public void hitTarget(LivingEntity e, float damage) {
        e.hurt(damageSources().mobAttack(this), (float) (damage * ModConfig.BOSS_DAMAGE_MULT.get()));
    }

    // ---- death, loot, progression ----------------------------------------------------------

    /** Players who dealt at least the configured share of max health. */
    public List<ServerPlayer> eligiblePlayers() {
        List<ServerPlayer> out = new ArrayList<>();
        if (!(level() instanceof ServerLevel sl)) return out;
        float need = (float) (getMaxHealth() * ModConfig.BOSS_LOOT_SHARE.get());
        damageBy.forEach((id, dmg) -> {
            if (dmg >= need && sl.getPlayerByUUID(id) instanceof ServerPlayer sp) out.add(sp);
        });
        return out;
    }

    /** Test hook: credits damage to a player as if dealt in combat. */
    public void creditDamage(Player p, float amount) {
        damageBy.merge(p.getUUID(), amount, Float::sum);
    }

    @Override
    public void die(DamageSource src) {
        if (!level().isClientSide) {
            List<ServerPlayer> players = eligiblePlayers();
            Constellations.Entry entry = Constellations.ALL.stream().filter(e -> e.boss().equals(bossId())).findFirst().orElse(null);
            for (ServerPlayer sp : players) {
                if (Progress.recordKill(sp, bossId()) && entry != null) {
                    sp.sendSystemMessage(Component.translatable("message.celestialascent.constellation",
                            Component.translatable("constellation.celestialascent." + entry.key())).withColor(entry.color()));
                }
            }
            if (getServer() != null) {
                getServer().getPlayerList().broadcastSystemMessage(
                        Component.translatable("message.celestialascent.boss_defeated", getDisplayName()).withColor(0xFFD966), false);
            }
        }
        super.die(src);
    }

    @Override
    protected void dropFromLootTable(DamageSource src, boolean byPlayer) {
        List<ServerPlayer> players = eligiblePlayers();
        if (players.isEmpty() || !(level() instanceof ServerLevel sl)) {
            super.dropFromLootTable(src, byPlayer);
            return;
        }
        LootTable table = sl.getServer().reloadableRegistries().getLootTable(getLootTable());
        for (ServerPlayer sp : players) {
            LootParams params = new LootParams.Builder(sl)
                    .withParameter(LootContextParams.THIS_ENTITY, this)
                    .withParameter(LootContextParams.ORIGIN, position())
                    .withParameter(LootContextParams.DAMAGE_SOURCE, src)
                    .withParameter(LootContextParams.ATTACKING_ENTITY, sp)
                    .withParameter(LootContextParams.LAST_DAMAGE_PLAYER, sp)
                    .withLuck(sp.getLuck())
                    .create(LootContextParamSets.ENTITY);
            for (ItemStack stack : table.getRandomItems(params)) {
                giveOwned(sl, sp, stack);
            }
        }
    }

    /** Drops a stack at the player's feet that only they can pick up. */
    public static void giveOwned(ServerLevel sl, ServerPlayer sp, ItemStack stack) {
        ItemEntity item = new ItemEntity(sl, sp.getX(), sp.getY() + 0.5, sp.getZ(), stack);
        item.setTarget(sp.getUUID());
        item.setPickUpDelay(10);
        item.setGlowingTag(true);
        sl.addFreshEntity(item);
    }

    @Override
    protected void tickDeath() {
        deathTime++;
        if (level() instanceof ServerLevel sl && deathTime % 4 == 0) {
            sl.sendParticles(ParticleTypes.EXPLOSION, getRandomX(1.5), getRandomY(), getRandomZ(1.5), 1, 0, 0, 0, 0);
        }
        if (deathTime >= DEATH_TICKS && !level().isClientSide && !isRemoved()) {
            level().broadcastEntityEvent(this, (byte) 60);
            remove(RemovalReason.KILLED);
        }
    }

    // ---- boss bar --------------------------------------------------------------------------

    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        bossEvent.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        bossEvent.removePlayer(player);
    }

    @Override
    public void setCustomName(Component name) {
        super.setCustomName(name);
        bossEvent.setName(getDisplayName());
    }

    // ---- persistence & anti-cheese flags ------------------------------------------------------

    @Override public boolean removeWhenFarAway(double d) { return false; }
    @Override public boolean requiresCustomPersistence() { return true; }
    @Override public void checkDespawn() {}
    @Override public boolean canBeLeashed() { return false; }
    @Override public boolean startRiding(Entity vehicle, boolean force) { return false; }
    @Override public boolean canChangeDimensions(Level from, Level to) { return false; }
    @Override public boolean isPushable() { return false; }
    @Override protected boolean shouldDespawnInPeaceful() { return false; }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Phase", phase());
        if (home != null) tag.put("Home", NbtUtils.writeBlockPos(home));
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(PHASE, tag.getInt("Phase"));
        NbtUtils.readBlockPos(tag, "Home").ifPresent(p -> home = p);
        if (hasCustomName()) bossEvent.setName(getDisplayName());
    }

    // ---- GeckoLib ----------------------------------------------------------------------------

    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("idle");
    private static final RawAnimation DEATH = RawAnimation.begin().thenPlayAndHold("death");

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        RawAnimation move = RawAnimation.begin().thenLoop(moveAnimation());
        controllers.add(new AnimationController<>(this, "main", 5, state -> {
            if (isDeadOrDying()) return state.setAndContinue(DEATH);
            if (isAttacking() || inTransition()) return PlayState.STOP;
            return state.setAndContinue(state.isMoving() ? move : IDLE);
        }));
        AnimationController<CelestialBoss> attack = new AnimationController<>(this, "attack", 2, state -> PlayState.STOP);
        attack.triggerableAnim("phase", RawAnimation.begin().thenPlay("phase"));
        for (BossAttack a : attacks) {
            if (a.animated) attack.triggerableAnim(a.id, RawAnimation.begin().thenPlay("attack." + a.id));
        }
        controllers.add(attack);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    /** Smooth yaw towards a point (used by attacks that aim). */
    public void faceTowards(Vec3 p) {
        double dx = p.x - getX(), dz = p.z - getZ();
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90f;
        setYRot(yaw);
        setYBodyRot(yaw);
        setYHeadRot(yaw);
    }
}
