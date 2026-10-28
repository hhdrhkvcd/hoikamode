# -*- coding: utf-8 -*-
"""The modern arsenal of Millennium Dawn: technologies and the Yugoslav equipment variants.

Generated from the Millennium Dawn history of Serbia (CC BY-SA 4.0).
"""

TECH_BLOCKS = [
    (
        'has_dlc = "No Step Back"',
        [
            'mbt_tech_ops',
            'tank_ammo_1',
            'tank_ammo_2',
            'defensive_systems',
            'nsb_gun_technology_1',
            'nsb_artillery_ammo_1',
            'nsb_special_ammo_1',
            'nsb_AA_autocannon_1',
            'nsb_SHORAD_missile_1',
            'mbt_tech',
            'mbt_tech_1',
            'mbt_tech_2',
            'defensive_systems_2',
            'nsb_gun_technology_2',
            'nsb_artillery_ammo_2',
            'nsb_artillery_ammo_3',
            'nsb_special_ammo_2',
            'nsb_special_ammo_3',
            'nsb_AA_autocannon_2',
            'nsb_SHORAD_missile_2',
            'tank_components_tech',
            'tank_components_tech_2',
            'small_medium_gun_tech',
            'medium_gun_tech',
            'armor_tech',
            'era_tech',
            'diesel_engine_tech',
            'diesel_engine_tech_2',
            'small_autocannon_tech',
            'nsb_artillery_1',
            'nsb_artillery_2',
            'nsb_arty_upgrade_1',
            'nsb_Anti_Air_0',
            'helo_ops_tech',
            'nsb_attack_helicopter_tech_1',
            'nsb_engine_tech_1',
            'nsb_atgm_tech_1',
            'nsb_multiple_atgm_tech_1',
            'nsb_heavy_atgm_tech_1',
            'nsb_rocket_pods_tech_1',
            'nsb_gun_pods_tech_1',
            'nsb_light_nose_gun_tech_1',
            'nsb_defense_tech_1',
            'nsb_transport_helicopter_2',
            'nsb_transport_helicopter_1',
        ],
    ),
    (
        'has_dlc = "By Blood Alone"',
        [
            'early_airframe_designs',
            'gen_3_light',
            'gen_4_light',
            'flying_wing_design',
            'engines_2',
            'refueling_1',
            'avionics_1',
            'awacs_1',
            'redundant_1',
            'early_weapons',
            'air_weapons_1',
            'countermeasures_1',
            'ag_weapons_1',
            'tgp_recon_1',
        ],
    ),
    (
        None,
        [
            'railway_system_01',
            'railway_system_02',
            'railway_system_03',
            'superior_firepower',
            'infantry_weapons_1',
            'infantry_weapons_2',
            'infantry_weapons_3',
            'infantry_weapons_4',
            'support_weapons',
            'support_weapons2',
            'tandem_charge_warheads',
            'squad_automatic_weapon',
            'cnc_equipment_1',
            'cnc_equipment_2',
            'Anti_tank_1',
            'Heavy_Anti_tank_1',
            'combat_eng_equipment',
            'util_vehicle_1',
            'util_vehicle_2',
            'util_vehicle_3',
            'night_vision_1',
            'night_vision_2',
            'body_armor_1',
            'basic_computing',
            'integrated_circuit',
            'computing_1',
            'radar',
            'internet_1',
            'internet_2',
            'gprs',
            'fuel_silos',
            'nanofibers_1',
            'nanofibers_2',
            'printing_1',
            'printing_2',
            'genetics_1',
            'fuel_refining',
            'early_renewables',
            'renewables',
            'electrification_1',
            'construction1',
            'corvette_hull_1',
            'corvette_hull_2',
            'frigate_hull_1',
            'frigate_hull_2',
            'frigate_hull_3',
            'destroyer_hull_1',
            'destroyer_hull_2',
            'attack_submarine_hull_1',
            'attack_submarine_hull_2',
            'tech_submarine_engineering_1',
            'tech_naval_systems_engineering',
            'tech_power_systems_1',
            'tech_combat_support_systems',
            'tech_fire_control_1',
            'tech_combat_radar_1',
            'tech_combat_radar_2',
            'tech_combat_sonar_1',
            'tech_early_naval_weapon_systems',
            'tech_naval_weapon_systems',
            'tech_light_guns_1',
            'tech_point_defense_chain_gun',
            'tech_point_defense_system_1',
            'tech_diesel_power_systems_1',
            'tech_turret_missiles_surface_1',
            'tech_turret_missiles_aa_1',
            'tech_vls_surface_1',
            'tech_vls_aa_1',
            'tech_torpedoes_1',
            'tech_landing_craft_1',
        ],
    ),
    (
        'NOT = { has_dlc = "La Resistance" }',
        [
            'decryption_1',
            'encryption_1',
        ],
    ),
    (
        'has_dlc = "Gotterdammerung"',
        [
            'air_defense',
            'SAM',
            'SAM0',
        ],
    ),
]

# Equipment variants of the Yugoslav army (M-84, BOV, Zastava, Orao, Galeb, Kotor, ...).
EQUIPMENT_VARIANTS = [
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "M-84"
		type = medium_tank_chassis_1
		parent_version = 0
		modules = {
			main_armament_slot = tank_medium_cannon
			secondary_armament_slot = afv_coax_machine_gun_2
			ammunition_load_slot = mixed_main_ammo_1
			turret_type_slot = tank_soviet_turret
			suspension_type_slot = tank_torsion_bar_suspension_medium
			armor_type_slot = tank_composite_armor_gen1
			engine_type_slot = tank_diesel_engine_gen2
			reload_type_slot = automatic_loading
			special_type_slot_1 = smoke_launchers
			special_type_slot_2 = additional_mg
			special_type_slot_4 = tank_battlestation_1
		}
		upgrades = {
			tank_nsb_armor_upgrade = 1
		}
		obsolete = yes
		icon = "GFX_SER_LAND_MBT2"
		design_team = mio:SER_yugoimport_spdr_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "M-84A"
		type = medium_tank_chassis_1
		parent_version = 0
		modules = {
			main_armament_slot = tank_medium_cannon
			secondary_armament_slot = afv_coax_machine_gun_2
			ammunition_load_slot = mixed_main_ammo_2
			turret_type_slot = tank_soviet_turret
			suspension_type_slot = tank_torsion_bar_suspension_medium
			armor_type_slot = tank_composite_armor_gen1
			engine_type_slot = tank_diesel_engine_gen2
			reload_type_slot = automatic_loading
			special_type_slot_1 = smoke_launchers
			special_type_slot_2 = additional_mg
			special_type_slot_4 = tank_battlestation_2
		}
		upgrades = {
			tank_nsb_armor_upgrade = 3
		}
		icon = "GFX_SER_LAND_MBT2_M84AB1"
		design_team = mio:SER_yugoimport_spdr_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "BOV"
		type = medium_tank_amphibious_chassis_1
		parent_version = 0
		modules = {
			main_armament_slot = afv_machine_gun_2
			reload_type_slot = automatic_loading
			ammunition_load_slot = machine_gun_ammo_1
			turret_type_slot = tank_base_tank_turret
			suspension_type_slot = tank_wheeled_suspension_light
			armor_type_slot = tank_steel_armor_gen2
			engine_type_slot = tank_diesel_engine_gen2
			special_type_slot_1 = afv_troop_capacity
			special_type_slot_4 = tank_battlestation_2
		}
		upgrades = {
			tank_nsb_armor_upgrade = 1
		}
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "M-60/PB"
		type = medium_tank_amphibious_chassis_1
		parent_version = 2
		modules = {
			main_armament_slot = afv_machine_gun
			reload_type_slot = automatic_loading
			ammunition_load_slot = machine_gun_ammo_1
			turret_type_slot = tank_base_tank_turret
			suspension_type_slot = tank_torsion_bar_suspension_light
			armor_type_slot = tank_steel_armor_gen1
			engine_type_slot = tank_diesel_engine_gen1
			special_type_slot_1 = afv_troop_capacity
			special_type_slot_4 = tank_battlestation_1
		}
		upgrades = {
			tank_nsb_armor_upgrade = 2
		}
		obsolete = yes
		icon = "GFX_SER_LAND_APC1_M60"
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "BVP M-80"
		type = medium_tank_flame_chassis_0
		parent_version = 0
		modules = {
			main_armament_slot = small_autocannon
			secondary_armament_slot = afv_coax_machine_gun_2
			reload_type_slot = automatic_loading
			ammunition_load_slot = mixed_autocannon_ammo_2
			turret_type_slot = tank_base_tank_turret
			suspension_type_slot = tank_torsion_bar_suspension_light
			armor_type_slot = tank_steel_armor_gen1
			engine_type_slot = tank_diesel_engine_gen1
			special_type_slot_4 = tank_battlestation_1
			special_type_slot_1 = afv_troop_capacity
		}
		upgrades = {
			tank_nsb_armor_upgrade = 1
		}
		obsolete = yes
		icon = "GFX_SER_LAND_IFV1"
		design_team = mio:SER_yugoimport_spdr_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "M-77"
		type = medium_tank_rocket_chassis_1
		parent_version = 0
		modules = {
			main_armament_slot = art_med_rocket_gen2
			turret_type_slot = tank_base_tank_turret
			reload_type_slot = eight_missile_pack
			ammunition_load_slot = artillery_medium_ammo_2
			suspension_type_slot = tank_wheeled_suspension_medium
			engine_type_slot = afv_gasoline_engine_gen2
			special_type_slot_1 = fire_ammo_2
			special_type_slot_4 = tank_battlestation_1
		}
		upgrades = {
			tank_nsb_fire_upgrade = 2
		}
		icon = "GFX_SER_LAND_SPR2"
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "M-63"
		type = medium_tank_rocket_chassis_0
		parent_version = 0
		modules = {
			main_armament_slot = art_med_rocket_gen1
			turret_type_slot = tank_base_tank_turret
			reload_type_slot = eight_missile_pack
			ammunition_load_slot = artillery_medium_ammo_1
			suspension_type_slot = tank_wheeled_suspension_medium
			engine_type_slot = afv_gasoline_engine_gen2
			special_type_slot_1 = fire_ammo_1
			special_type_slot_4 = tank_battlestation_1
		}
		upgrades = {
			tank_nsb_fire_upgrade = 2
		}
		icon = "GFX_SER_LAND_SPR1"
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Nora B-52"
		type = medium_tank_artillery_chassis_2
		parent_version = 0
		modules = {
			main_armament_slot = art_med_gun_gen2
			reload_type_slot = automatic_loading
			ammunition_load_slot = artillery_medium_ammo_2
			turret_type_slot = tank_base_tank_turret
			suspension_type_slot = tank_wheeled_suspension_medium
			engine_type_slot = tank_diesel_engine_gen1
			special_type_slot_1 = empty
			special_type_slot_2 = empty
			special_type_slot_4 = tank_battlestation_2
		}
		upgrades = {
			tank_nsb_fire_upgrade = 1
		}
		icon = "GFX_SER_LAND_SPG2"
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Zastava M70"
		type = infantry_weapons_1
		upgrades = {
			inf_eq_heavy_weapons = 1
			inf_eq_mortars = 1
			inf_eq_gadjets = 1
		}
		mark_older_equipment_obsolete = yes
		design_team = mio:SER_zastava_arms_materiel_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Zastava M59/66"
		type = infantry_weapons_1
		upgrades = {
		}
		obsolete = yes
		design_team = mio:SER_zastava_arms_materiel_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Zastava M56"
		type = infantry_weapons_1
		upgrades = {
			inf_eq_heavy_weapons = 1
		}
		obsolete = yes
		design_team = mio:SER_zastava_arms_materiel_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Zastava M70B1N"
		type = infantry_weapons_2
		upgrades = {
			inf_eq_heavy_weapons = 1
			inf_eq_gadjets = 1
		}
		mark_older_equipment_obsolete = yes
		design_team = mio:SER_zastava_arms_materiel_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Zastava M80"
		type = infantry_weapons_3
		upgrades = {
			inf_eq_heavy_weapons = 1
			inf_eq_gadjets = 1
		}
		mark_older_equipment_obsolete = yes
		design_team = mio:SER_zastava_arms_materiel_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Zastava M90"
		type = infantry_weapons_4
		upgrades = {
			inf_eq_heavy_weapons = 2
			inf_eq_gadjets = 2
			inf_eq_cutting_corners = 1
		}
		mark_older_equipment_obsolete = yes
		design_team = mio:SER_zastava_arms_materiel_manufacturer
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "Zastava M55"
		type = Anti_Air_0
		upgrades = {
			AA_fire_control = 1
		}
		icon = "GFX_SER_LAND_M55"
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "M48"
		type = artillery_1
		icon = "GFX_SER_LAND_M48"
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "No Step Back"',
        """
create_equipment_variant = {
		name = "M56"
		type = artillery_1
		upgrades = {
			L_arty_warhead = 1
		}
		icon = "GFX_SER_LAND_M56"
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "By Blood Alone"',
        """
create_equipment_variant = {
		name = "G-2 Galeb"
		type = small_plane_strike_airframe_1
		parent_version = 0
		modules = {
			fixed_main_weapon_slot = weap_mp_med_hardpoint_1
			fixed_gun_slot = weap_multi_gun_2
			engine_type_slot = engine_light_single_1
			avionics_type_slot = avionics_manned_1
			wingform_type_slot = wing_straight
			special_slot_type_1 = empty
			special_slot_type_2 = empty
		}
		icon = "GFX_SER_AIR_G_2"
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "By Blood Alone"',
        """
create_equipment_variant = {
		name = "J-21 Jastreb"
		type = small_plane_strike_airframe_1
		parent_version = 0
		modules = {
			fixed_main_weapon_slot = weap_mp_med_hardpoint_1
			fixed_gun_slot = weap_multi_gun_2
			engine_type_slot = engine_light_single_1
			avionics_type_slot = avionics_manned_1
			wingform_type_slot = wing_straight
			special_slot_type_1 = spec_countermeasures_1
			special_slot_type_2 = spec_tgp_1
		}
		icon = "GFX_SER_AIR_J_21"
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "By Blood Alone"',
        """
create_equipment_variant = {
		name = "J-22 Orao"
		type = small_plane_strike_airframe_1
		parent_version = 0
		modules = {
			fixed_main_weapon_slot = weap_mp_med_hardpoint_1
			fixed_gun_slot = weap_multi_gun_2
			engine_type_slot = engine_light_double_1
			avionics_type_slot = avionics_manned_1
			wingform_type_slot = wing_swept
			special_slot_type_1 = spec_countermeasures_1
			special_slot_type_2 = spec_tgp_1
		}
		icon = "GFX_SER_AIR_J_22"
		obsolete = yes
	}
        """,
    ),
    (
        'has_dlc = "By Blood Alone"',
        """
create_equipment_variant = {
		name = "G-4 Super Galeb"
		type = small_plane_strike_airframe_2
		parent_version = 0
		modules = {
			fixed_main_weapon_slot = weap_mp_light_hardpoint_1
			fixed_gun_slot = weap_multi_gun_2
			engine_type_slot = engine_light_single_2
			avionics_type_slot = avionics_manned_1
			wingform_type_slot = wing_swept
			special_slot_type_1 = spec_countermeasures_1
			special_slot_type_2 = spec_tgp_1
		}
		icon = "GFX_SER_AIR_G_4"
		obsolete = yes
	}
        """,
    ),
    (
        None,
        """
create_equipment_variant = {
		name = "Kotor Class"
		type = corvette_hull_2
		parent_version = 0
		modules = {
			fixed_ship_engine_slot = module_light_surface_diesel_power_1
			fixed_ship_fire_control_system_slot = module_analog_fire_control
			fixed_ship_radar_slot = module_radar_1
			fixed_ship_auxillary_slot = module_naval_missile_mount_quad
			fixed_ship_battery_slot = module_76mm_gun_1
			front_1_custom_slot = module_ciws_1
			rear_1_custom_slot = module_naval_missile_mount_quad
			fixed_ship_missile_ammo_slot = module_naval_ammo_balanced_1
		}
		obsolete = yes
		role_icon_index = 12
	}
        """,
    ),
    (
        None,
        """
create_equipment_variant = {
		name = "Heroj Class"
		type = attack_submarine_hull_1
		parent_version = 0
		modules = {
			fixed_ship_engine_slot = module_sub_diesel_electric_power
			fixed_ship_radar_slot = module_sonar_1
			fixed_ship_auxillary_slot_1 = module_minelaying
			fixed_ship_auxillary_slot = module_torpedoes_1
			fixed_ship_battery_slot = module_anti_ship_torpedoes_1
		}
		obsolete = yes
		role_icon_index = 27
	}
        """,
    ),
]
