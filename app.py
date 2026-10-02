from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

load_dotenv()

app = Flask(__name__)
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
NASA_NEO_URL = "https://api.nasa.gov/neo/rest/v1/feed"

BASE_OBJECTS: List[Dict[str, Any]] = [
    {
        "id": "sun",
        "name": "Sun",
        "type": "star",
        "category": "G-type main-sequence star",
        "coordinates": {"x": 0, "y": 0, "z": 0},
        "distance_au": 0.0,
        "description": "The Sun is the star at the center of the Solar System and the main source of energy for Earth.",
        "life_probability": 0.62,
        "life_types": {"carbon_based": 0.62, "silicon_based": 0.18, "ammonia_based": 0.07, "unknown": 0.13},
        "elements": ["Hydrogen", "Helium", "Oxygen", "Carbon", "Iron"],
        "temperature_k": 5778,
        "image_url": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg",
        "image_caption": "Current SDO HMI visible-light continuum image of the solar photosphere.",
    },
    {
        "id": "mercury",
        "name": "Mercury",
        "type": "planet",
        "category": "Rocky inner planet",
        "coordinates": {"x": 80, "y": 20, "z": 110},
        "distance_au": 0.39,
        "description": "Mercury is the smallest planet and the closest world to the Sun, with extreme temperature swings.",
        "life_probability": 0.02,
        "elements": ["Silicates", "Iron", "Oxygen", "Magnesium", "Sulfur"],
        "temperature_k": 440,
        "image_url": "https://images-assets.nasa.gov/image/PIA11245/PIA11245~orig.jpg",
    },
    {
        "id": "venus",
        "name": "Venus",
        "type": "planet",
        "category": "Dense atmosphere planet",
        "coordinates": {"x": 120, "y": 50, "z": 140},
        "distance_au": 0.72,
        "description": "Venus is a cloud-wrapped world with intense heat and a thick carbon-dioxide atmosphere.",
        "life_types": {"carbon_based": 0.05, "silicon_based": 0.08, "ammonia_based": 0.04, "unknown": 0.83},
        "elements": ["Carbon dioxide", "Nitrogen", "Sulfur dioxide", "Silicates", "Iron"],
        "temperature_k": 735,
        "image_url": "https://images-assets.nasa.gov/image/PIA23791/PIA23791~orig.jpg",
    },
    {
        "id": "earth",
        "name": "Earth",
        "type": "planet",
        "category": "Rocky planet",
        "coordinates": {"x": 180, "y": 40, "z": 200},
        "distance_au": 1.0,
        "description": "Earth is a water-rich world with an atmosphere and biosphere that sustain complex life.",
        "life_probability": 0.96,
        "life_types": {"carbon_based": 0.96, "silicon_based": 0.22, "ammonia_based": 0.12, "unknown": 0.08},
        "elements": ["Oxygen", "Silicon", "Iron", "Carbon", "Nitrogen"],
        "temperature_k": 288,
        "image_url": "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e000496/GSFC_20171208_Archive_e000496~small.jpg",
        "image_caption": "Earthrise composite captured by NASA's Lunar Reconnaissance Orbiter.",
    },
    {
        "id": "moon",
        "name": "Moon",
        "type": "moon",
        "category": "Earth natural satellite",
        "coordinates": {"x": 200, "y": 10, "z": 220},
        "distance_au": 0.00257,
        "description": "Earth's Moon preserves clues about the early history of the Solar System and the formation of terrestrial planets.",
        "life_probability": 0.05,
        "life_types": {"carbon_based": 0.05, "silicon_based": 0.18, "ammonia_based": 0.03, "unknown": 0.74},
        "elements": ["Silicates", "Iron", "Oxygen", "Titanium", "Magnesium"],
        "temperature_k": 220,
        "image_url": "https://nssdc.gsfc.nasa.gov/planetary/image/moon.jpg",
    },
    {
        "id": "mars",
        "name": "Mars",
        "type": "planet",
        "category": "Desert planet",
        "coordinates": {"x": 240, "y": -60, "z": 160},
        "distance_au": 1.52,
        "description": "Mars has polar ice, dry canyons, and evidence of ancient water that makes it a key life-search target.",
        "life_probability": 0.42,
        "life_types": {"carbon_based": 0.42, "silicon_based": 0.31, "ammonia_based": 0.19, "unknown": 0.08},
        "elements": ["Iron", "Silicon", "Magnesium", "Sulfur", "Oxygen"],
        "temperature_k": 210,
        "image_url": "https://images-assets.nasa.gov/image/PIA00003/PIA00003~small.jpg",
        "image_caption": "Viking Orbiter mosaic covering nearly a full hemisphere of Mars.",
    },
    {
        "id": "phobos",
        "name": "Phobos",
        "type": "moon",
        "category": "Mars moon",
        "image_url": "https://images-assets.nasa.gov/image/PIA23204/PIA23204~orig.jpg",
        "image_caption": "THEMIS infrared image of Phobos; colors show surface temperature.",
        "coordinates": {"x": 250, "y": -80, "z": 150},
        "distance_au": 1.52,
        "description": "Phobos is the larger of Mars's two moons and is a heavily cratered, irregularly shaped body.",
        "life_probability": 0.02,
        "life_types": {"carbon_based": 0.02, "silicon_based": 0.16, "ammonia_based": 0.02, "unknown": 0.80},
        "elements": ["Silicates", "Iron", "Magnesium", "Oxygen", "Carbon"],
        "temperature_k": 233,
    },
    {
        "id": "deimos",
        "name": "Deimos",
        "type": "moon",
        "image_url": "https://images-assets.nasa.gov/image/PIA00034/PIA00034~orig.jpg",
        "category": "Mars moon",
        "coordinates": {"x": 270, "y": -120, "z": 180},
        "distance_au": 1.52,
        "description": "Deimos is a small, smooth outer moon of Mars with a low-gravity surface.",
        "life_probability": 0.02,
        "life_types": {"carbon_based": 0.02, "silicon_based": 0.15, "ammonia_based": 0.02, "unknown": 0.81},
        "elements": ["Silicates", "Iron", "Magnesium", "Oxygen", "Carbon"],
        "temperature_k": 233,
        "image_url": "https://images-assets.nasa.gov/image/PIA11802/PIA11802~orig.jpg",
    },
    {
        "id": "ceres",
        "name": "Ceres",
        "type": "dwarf_planet",
        "category": "Dwarf planet",
        "coordinates": {"x": 120, "y": -170, "z": 50},
        "distance_au": 2.77,
        "description": "Ceres is the largest object in the asteroid belt and contains water-rich minerals in its crust.",
        "life_probability": 0.12,
        "life_types": {"carbon_based": 0.12, "silicon_based": 0.23, "ammonia_based": 0.06, "unknown": 0.59},
        "elements": ["Water ice", "Silicates", "Carbon", "Iron", "Magnesium"],
        "temperature_k": 167,
        "image_url": "https://images-assets.nasa.gov/image/PIA21906/PIA21906~small.jpg",
        "image_caption": "Dawn orthographic view of Ceres centered on Occator Crater.",
    },
    {
        "id": "vesta",
        "name": "Vesta",
        "type": "asteroid",
        "category": "Asteroid belt member",
        "coordinates": {"x": 150, "y": -210, "z": 100},
        "distance_au": 2.36,
        "description": "Vesta is one of the largest bodies in the asteroid belt and preserves a differentiated rocky interior.",
        "life_probability": 0.03,
        "life_types": {"carbon_based": 0.03, "silicon_based": 0.22, "ammonia_based": 0.01, "unknown": 0.74},
        "elements": ["Silicates", "Iron", "Magnesium", "Calcium", "Aluminum"],
        "temperature_k": 180,
        "image_url": "https://images-assets.nasa.gov/image/PIA15140/PIA15140~orig.jpg",
        "image_caption": "NASA Dawn stereoscopic image of asteroid Vesta.",
    },
    {
        "id": "pallas",
        "name": "Pallas",
        "type": "asteroid",
        "category": "Asteroid belt member",
        "coordinates": {"x": 80, "y": -240, "z": -70},
        "distance_au": 2.77,
        "description": "Pallas is a large irregular asteroid in the main belt, notable for its unusual tilt and composition.",
        "life_probability": 0.02,
        "life_types": {"carbon_based": 0.03, "silicon_based": 0.21, "ammonia_based": 0.01, "unknown": 0.75},
        "elements": ["Silicates", "Iron", "Nickel", "Magnesium", "Carbon"],
        "temperature_k": 170,
        "image_url": "https://images-assets.nasa.gov/image/PIA19647/PIA19647~orig.jpg",
    },
    {
        "id": "hygiea",
        "name": "Hygiea",
        "type": "asteroid",
        "category": "Large asteroid belt body",
        "coordinates": {"x": 200, "y": -150, "z": 60},
        "distance_au": 3.14,
        "description": "Hygiea is a large, nearly spherical asteroid in the main belt and one of the largest minor planets.",
        "life_probability": 0.02,
        "life_types": {"carbon_based": 0.04, "silicon_based": 0.18, "ammonia_based": 0.01, "unknown": 0.77},
        "elements": ["Silicates", "Carbon", "Iron", "Magnesium", "Oxygen"],
        "temperature_k": 160,
        "image_url": "https://images-assets.nasa.gov/image/PIA19862/PIA19862~orig.jpg",
    },
    {
        "id": "jupiter",
        "name": "Jupiter",
        "type": "planet",
        "category": "Gas giant",
        "coordinates": {"x": -210, "y": -120, "z": -120},
        "distance_au": 5.2,
        "description": "Jupiter is the largest planet in the Solar System, marked by storms, bands, and many moons.",
        "life_probability": 0.08,
        "life_types": {"carbon_based": 0.08, "silicon_based": 0.06, "ammonia_based": 0.09, "unknown": 0.77},
        "elements": ["Hydrogen", "Helium", "Methane", "Ammonia", "Water"],
        "temperature_k": 165,
        "image_url": "https://images-assets.nasa.gov/image/PIA02873/PIA02873~orig.jpg",
    },
    {
        "id": "io",
        "name": "Io",
        "type": "moon",
        "category": "Volcanic moon",
        "coordinates": {"x": -180, "y": -40, "z": -80},
        "distance_au": 5.9,
        "description": "Io is the most volcanically active moon in the Solar System, shaped by intense tidal heating.",
        "life_probability": 0.04,
        "life_types": {"carbon_based": 0.04, "silicon_based": 0.11, "ammonia_based": 0.02, "unknown": 0.83},
        "elements": ["Sulfur", "Silicates", "Oxygen", "Magnesium", "Iron"],
        "temperature_k": 110,
        "image_url": "https://images-assets.nasa.gov/image/PIA01667/PIA01667~orig.jpg",
    },
    {
        "id": "europa",
        "name": "Europa",
        "type": "moon",
        "category": "Ice moon",
        "coordinates": {"x": -260, "y": 110, "z": -50},
        "distance_au": 5.4,
        "description": "Europa is an icy moon with a suspected subsurface ocean and strong potential for microbial chemistry.",
        "life_probability": 0.58,
        "life_types": {"carbon_based": 0.58, "silicon_based": 0.16, "ammonia_based": 0.11, "unknown": 0.15},
        "elements": ["Water ice", "Silicates", "Magnesium", "Oxygen", "Sulfur"],
        "temperature_k": 110,
        "image_url": "https://images-assets.nasa.gov/image/PIA00502/PIA00502~orig.jpg",
    },
    {
        "id": "ganymede",
        "name": "Ganymede",
        "type": "moon",
        "category": "Largest moon in the Solar System",
        "coordinates": {"x": -300, "y": 20, "z": -130},
        "distance_au": 5.27,
        "description": "Ganymede is the largest moon in the Solar System and is larger than Mercury, with a layered interior.",
        "life_probability": 0.12,
        "life_types": {"carbon_based": 0.12, "silicon_based": 0.19, "ammonia_based": 0.06, "unknown": 0.63},
        "elements": ["Silicates", "Iron", "Water ice", "Oxygen", "Magnesium"],
        "temperature_k": 110,
        "image_url": "https://images-assets.nasa.gov/image/PIA01494/PIA01494~orig.jpg",
    },
    {
        "id": "callisto",
        "name": "Callisto",
        "type": "moon",
        "category": "Heavily cratered moon",
        "coordinates": {"x": -340, "y": -90, "z": -180},
        "distance_au": 5.4,
        "description": "Callisto is an ancient, heavily cratered moon with a complex surface history and deep ice-rock mix.",
        "life_probability": 0.07,
        "life_types": {"carbon_based": 0.07, "silicon_based": 0.14, "ammonia_based": 0.04, "unknown": 0.75},
        "elements": ["Silicates", "Water ice", "Iron", "Carbon", "Magnesium"],
        "temperature_k": 134,
        "image_url": "https://images-assets.nasa.gov/image/PIA01478/PIA01478~orig.jpg",
    },
    {
        "id": "saturn",
        "name": "Saturn",
        "type": "planet",
        "category": "Ringed giant",
        "coordinates": {"x": -290, "y": 40, "z": -200},
        "distance_au": 9.58,
        "description": "Saturn is ringed with icy particles and hosts dozens of moons, including Titan and Enceladus.",
        "life_probability": 0.11,
        "life_types": {"carbon_based": 0.11, "silicon_based": 0.08, "ammonia_based": 0.09, "unknown": 0.72},
        "elements": ["Hydrogen", "Helium", "Water ice", "Methane", "Ammonia"],
        "temperature_k": 134,
        "image_url": "https://images-assets.nasa.gov/image/PIA17172/PIA17172~orig.jpg",
    },
    {
        "id": "titan",
        "name": "Titan",
        "type": "moon",
        "category": "Methane-rich moon",
        "coordinates": {"x": -90, "y": 170, "z": -90},
        "distance_au": 9.54,
        "description": "Titan is a hazy moon with methane-rich weather and a dense atmosphere full of organic chemistry.",
        "life_probability": 0.37,
        "life_types": {"carbon_based": 0.37, "silicon_based": 0.13, "ammonia_based": 0.21, "unknown": 0.29},
        "elements": ["Nitrogen", "Methane", "Ethane", "Carbon", "Hydrogen"],
        "temperature_k": 94,
        "image_url": "https://images-assets.nasa.gov/image/PIA16177/PIA16177~small.jpg",
    },
    {
        "id": "enceladus",
        "name": "Enceladus",
        "type": "moon",
        "category": "Icy geyser moon",
        "coordinates": {"x": -240, "y": 90, "z": -250},
        "distance_au": 9.5,
        "description": "Enceladus sprays water ice from geysers through a subsurface ocean, making it one of the most compelling habitability targets.",
        "life_probability": 0.55,
        "life_types": {"carbon_based": 0.55, "silicon_based": 0.12, "ammonia_based": 0.13, "unknown": 0.20},
        "elements": ["Water ice", "Silicates", "Hydrogen", "Oxygen", "Carbon"],
        "temperature_k": 75,
        "image_url": "https://images-assets.nasa.gov/image/PIA21485/PIA21485~orig.jpg",
    },
    {
        "id": "rhea",
        "name": "Rhea",
        "type": "moon",
        "category": "Icy moon",
        "coordinates": {"x": -330, "y": 120, "z": -240},
        "distance_au": 9.58,
        "description": "Rhea is an icy moon with a heavily cratered surface and a dark, ancient crust.",
        "life_probability": 0.08,
        "life_types": {"carbon_based": 0.08, "silicon_based": 0.11, "ammonia_based": 0.03, "unknown": 0.78},
        "elements": ["Water ice", "Silicates", "Carbon", "Oxygen", "Iron"],
        "temperature_k": 99,
        "image_url": "https://images-assets.nasa.gov/image/PIA08298/PIA08298~orig.jpg",
    },
    {
        "id": "iapetus",
        "name": "Iapetus",
        "type": "moon",
        "category": "Two-tone moon",
        "coordinates": {"x": -360, "y": 10, "z": -310},
        "distance_au": 9.55,
        "description": "Iapetus has a striking two-tone surface and one of the most dramatic albedo contrasts in the Solar System.",
        "life_probability": 0.07,
        "life_types": {"carbon_based": 0.07, "silicon_based": 0.13, "ammonia_based": 0.02, "unknown": 0.78},
        "elements": ["Water ice", "Silicates", "Carbon", "Iron", "Oxygen"],
        "temperature_k": 130,
        "image_url": "https://images-assets.nasa.gov/image/PIA08328/PIA08328~orig.jpg",
    },
    {
        "id": "uranus",
        "name": "Uranus",
        "type": "planet",
        "category": "Ice giant",
        "coordinates": {"x": 300, "y": -120, "z": -260},
        "distance_au": 19.2,
        "description": "Uranus rotates on its side and is made of icy materials and a hydrogen-helium envelope.",
        "life_probability": 0.07,
        "life_types": {"carbon_based": 0.07, "silicon_based": 0.06, "ammonia_based": 0.11, "unknown": 0.76},
        "elements": ["Hydrogen", "Helium", "Water", "Ammonia", "Methane"],
        "temperature_k": 76,
        "image_url": "https://images-assets.nasa.gov/image/PIA18182/PIA18182~orig.jpg",
    },
    {
        "id": "titania",
        "name": "Titania",
        "type": "moon",
        "category": "Uranian moon",
        "coordinates": {"x": 330, "y": -150, "z": -290},
        "distance_au": 19.2,
        "description": "Titania is the largest moon of Uranus and shows tectonic features and icy ridges.",
        "life_probability": 0.06,
        "life_types": {"carbon_based": 0.06, "silicon_based": 0.10, "ammonia_based": 0.03, "unknown": 0.81},
        "elements": ["Water ice", "Silicates", "Carbon", "Oxygen", "Iron"],
        "temperature_k": 70,
        "image_url": "https://images-assets.nasa.gov/image/PIA00039/PIA00039~orig.jpg",
    },
    {
        "id": "oberon",
        "name": "Oberon",
        "type": "moon",
        "category": "Uranian moon",
        "coordinates": {"x": 370, "y": -70, "z": -330},
        "distance_au": 19.4,
        "description": "Oberon is a dark, ancient moon of Uranus with scarps and impact basins across its icy crust.",
        "life_probability": 0.05,
        "life_types": {"carbon_based": 0.05, "silicon_based": 0.09, "ammonia_based": 0.02, "unknown": 0.84},
        "elements": ["Water ice", "Silicates", "Carbon", "Iron", "Oxygen"],
        "temperature_k": 60,
        "image_url": "https://images-assets.nasa.gov/image/PIA00040/PIA00040~orig.jpg",
    },
    {
        "id": "miranda",
        "name": "Miranda",
        "type": "moon",
        "category": "Uranian moon",
        "coordinates": {"x": 410, "y": -200, "z": -250},
        "distance_au": 19.2,
        "description": "Miranda displays fractured cliffs and ice ridges, suggesting a complex and dynamic geologic past.",
        "life_probability": 0.05,
        "life_types": {"carbon_based": 0.05, "silicon_based": 0.10, "ammonia_based": 0.03, "unknown": 0.82},
        "elements": ["Water ice", "Silicates", "Carbon", "Oxygen", "Iron"],
        "temperature_k": 61,
        "image_url": "https://images-assets.nasa.gov/image/PIA00043/PIA00043~orig.jpg",
    },
    {
        "id": "neptune",
        "name": "Neptune",
        "type": "planet",
        "category": "Ice giant",
        "coordinates": {"x": 380, "y": 130, "z": -340},
        "distance_au": 30.1,
        "description": "Neptune is a windy ice giant with strong storms and a distant orbit beyond Uranus.",
        "life_probability": 0.06,
        "life_types": {"carbon_based": 0.06, "silicon_based": 0.05, "ammonia_based": 0.10, "unknown": 0.79},
        "elements": ["Hydrogen", "Helium", "Methane", "Water", "Ammonia"],
        "temperature_k": 72,
        "image_url": "https://images-assets.nasa.gov/image/PIA01492/PIA01492~orig.jpg",
    },
    {
        "id": "triton",
        "name": "Triton",
        "type": "moon",
        "category": "Captured ice moon",
        "coordinates": {"x": 420, "y": 150, "z": -370},
        "distance_au": 30.1,
        "description": "Triton is Neptune's large moon and is thought to be a captured object from the Kuiper Belt.",
        "life_probability": 0.09,
        "life_types": {"carbon_based": 0.09, "silicon_based": 0.08, "ammonia_based": 0.12, "unknown": 0.71},
        "elements": ["Nitrogen", "Water ice", "Carbon dioxide", "Methane", "Silicates"],
        "temperature_k": 38,
        "image_url": "https://images-assets.nasa.gov/image/PIA02203/PIA02203~orig.jpg",
    },
    {
        "id": "proteus",
        "name": "Proteus",
        "type": "moon",
        "category": "Neptunian moon",
        "coordinates": {"x": 330, "y": 190, "z": -400},
        "distance_au": 30.2,
        "description": "Proteus is an irregularly shaped moon of Neptune with a dark, heavily cratered surface.",
        "life_probability": 0.04,
        "life_types": {"carbon_based": 0.04, "silicon_based": 0.10, "ammonia_based": 0.03, "unknown": 0.83},
        "elements": ["Silicates", "Carbon", "Water ice", "Oxygen", "Iron"],
        "temperature_k": 50,
        "image_url": "https://images-assets.nasa.gov/image/PIA00018/PIA00018~orig.jpg",
    },
    {
        "id": "pluto",
        "name": "Pluto",
        "type": "dwarf_planet",
        "category": "Trans-Neptunian dwarf planet",
        "coordinates": {"x": -510, "y": -160, "z": 260},
        "distance_au": 39.5,
        "description": "Pluto is a large dwarf planet in the Kuiper Belt with a nitrogen-rich atmosphere and frozen heart.",
        "life_probability": 0.10,
        "life_types": {"carbon_based": 0.10, "silicon_based": 0.15, "ammonia_based": 0.05, "unknown": 0.70},
        "elements": ["Nitrogen", "Methane", "Water ice", "Carbon monoxide", "Silicates"],
        "temperature_k": 44,
        "image_url": "https://images-assets.nasa.gov/image/PIA19948/PIA19948~orig.jpg",
    },
    {
        "id": "charon",
        "name": "Charon",
        "type": "moon",
        "category": "Pluto moon",
        "coordinates": {"x": -560, "y": -120, "z": 290},
        "distance_au": 39.5,
        "description": "Charon is Pluto's large moon and the system's most prominent companion, with a frozen surface.",
        "life_probability": 0.06,
        "life_types": {"carbon_based": 0.06, "silicon_based": 0.12, "ammonia_based": 0.03, "unknown": 0.79},
        "elements": ["Water ice", "Silicates", "Carbon", "Nitrogen", "Oxygen"],
        "temperature_k": 55,
        "image_url": "https://images-assets.nasa.gov/image/PIA19931/PIA19931~orig.jpg",
    },
    {
        "id": "haumea",
        "name": "Haumea",
        "type": "dwarf_planet",
        "category": "Fast-rotating Kuiper Belt dwarf",
        "coordinates": {"x": -650, "y": 150, "z": 330},
        "distance_au": 43.1,
        "description": "Haumea is a stretched, rapidly rotating dwarf planet in the Kuiper Belt with an icy surface.",
        "life_probability": 0.08,
        "life_types": {"carbon_based": 0.08, "silicon_based": 0.13, "ammonia_based": 0.04, "unknown": 0.75},
        "elements": ["Water ice", "Silicates", "Carbon", "Methane", "Oxygen"],
        "temperature_k": 32,
        "image_url": "https://images-assets.nasa.gov/image/PIA20177/PIA20177~orig.jpg",
    },
    {
        "id": "makemake",
        "name": "Makemake",
        "type": "dwarf_planet",
        "category": "Kuiper Belt dwarf planet",
        "coordinates": {"x": -700, "y": -60, "z": 390},
        "distance_au": 45.8,
        "description": "Makemake is a bright icy dwarf planet in the outer Solar System with a methane-rich surface.",
        "life_probability": 0.09,
        "life_types": {"carbon_based": 0.09, "silicon_based": 0.12, "ammonia_based": 0.04, "unknown": 0.75},
        "elements": ["Methane", "Water ice", "Nitrogen", "Silicates", "Carbon"],
        "temperature_k": 30,
        "image_url": "https://images-assets.nasa.gov/image/PIA20470/PIA20470~orig.jpg",
    },
    {
        "id": "eris",
        "name": "Eris",
        "type": "dwarf_planet",
        "category": "Scattered-disk dwarf planet",
        "coordinates": {"x": -760, "y": 90, "z": 460},
        "distance_au": 67.7,
        "description": "Eris is a distant trans-Neptunian dwarf planet orbiting beyond Pluto and among the most massive known.",
        "life_probability": 0.07,
        "life_types": {"carbon_based": 0.07, "silicon_based": 0.11, "ammonia_based": 0.03, "unknown": 0.79},
        "elements": ["Methane", "Water ice", "Carbon monoxide", "Silicates", "Nitrogen"],
        "temperature_k": 25,
        "image_url": "https://images-assets.nasa.gov/image/PIA19873/PIA19873~orig.jpg",
    },
    {
        "id": "halley",
        "name": "Halley's Comet",
        "type": "comet",
        "category": "Period comet",
        "coordinates": {"x": 350, "y": 200, "z": -250},
        "distance_au": 35.1,
        "description": "Halley's Comet is a bright, periodic comet that has been visible from Earth for centuries.",
        "life_probability": 0.19,
        "life_types": {"carbon_based": 0.19, "silicon_based": 0.08, "ammonia_based": 0.12, "unknown": 0.61},
        "elements": ["Water", "Carbon dioxide", "Methane", "Silicates", "Iron"],
        "temperature_k": 120,
        "image_url": "https://images-assets.nasa.gov/image/PIA17485/PIA17485~small.jpg",
    },
    {
        "id": "hale-bopp",
        "name": "Hale-Bopp",
        "type": "comet",
        "category": "Long-period comet",
        "coordinates": {"x": 480, "y": 160, "z": 200},
        "distance_au": 52.0,
        "description": "Hale-Bopp is a bright long-period comet with a large coma and dust tail visible from Earth.",
        "life_probability": 0.14,
        "life_types": {"carbon_based": 0.14, "silicon_based": 0.07, "ammonia_based": 0.11, "unknown": 0.68},
        "elements": ["Water", "Carbon monoxide", "Methane", "Dust", "Silicates"],
        "temperature_k": 115,
        "image_url": "https://images-assets.nasa.gov/image/PIA01289/PIA01289~small.jpg",
    },
    {
        "id": "neowise",
        "name": "C/2020 F3 NEOWISE",
        "type": "comet",
        "category": "Long-period comet",
        "coordinates": {"x": -500, "y": 60, "z": 220},
        "distance_au": 46.7,
        "description": "NEOWISE was a bright comet visible to the naked eye and an important object for studying cometary composition.",
        "life_probability": 0.14,
        "life_types": {"carbon_based": 0.14, "silicon_based": 0.07, "ammonia_based": 0.12, "unknown": 0.67},
        "elements": ["Water", "Carbon monoxide", "Methane", "Dust", "Silicates"],
        "temperature_k": 110,
        "image_url": "https://images-assets.nasa.gov/image/NHQ202007120001/NHQ202007120001~small.jpg",
    },
]


EXPANDED_OBJECTS = BASE_OBJECTS


NASA_OBJECT_IMAGES: Dict[str, Dict[str, Any]] = {
    "sun": {"image_url": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg", "image_caption": "Current SDO HMI visible-light continuum image of the solar photosphere."},
    "mercury": {"image_url": "https://images-assets.nasa.gov/image/PIA11245/PIA11245~orig.jpg"},
    "venus": {"image_url": "https://images-assets.nasa.gov/image/PIA23791/PIA23791~orig.jpg", "image_caption": "Mariner 10 orange and ultraviolet filters combined as a false-color composite."},
    "earth": {"image_url": "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e000496/GSFC_20171208_Archive_e000496~small.jpg", "image_caption": "Earthrise composite captured by NASA's Lunar Reconnaissance Orbiter."},
    "moon": {"image_url": "https://nssdc.gsfc.nasa.gov/planetary/image/moon.jpg"},
    "mars": {"image_url": "https://images-assets.nasa.gov/image/PIA00003/PIA00003~small.jpg", "image_caption": "Viking Orbiter mosaic covering nearly a full hemisphere of Mars."},
    "phobos": {"image_url": "https://images-assets.nasa.gov/image/PIA23204/PIA23204~orig.jpg", "image_caption": "THEMIS infrared image; colors represent surface temperature."},
    "deimos": {"image_url": "https://images-assets.nasa.gov/image/PIA12290/PIA12290~small.jpg"},
    "ceres": {"image_url": "https://images-assets.nasa.gov/image/PIA21906/PIA21906~small.jpg", "image_caption": "Dawn orthographic view centered on Occator Crater."},
    "vesta": {"image_url": "https://images-assets.nasa.gov/image/PIA15140/PIA15140~orig.jpg", "image_caption": "Dawn stereoscopic image of Vesta."},
    "pallas": {"image_url": None},
    "hygiea": {"image_url": None},
    "jupiter": {"image_url": "https://images-assets.nasa.gov/image/PIA02873/PIA02873~orig.jpg", "image_caption": "Cassini true-color simulated globe assembled from spacecraft images."},
    "io": {"image_url": "https://images-assets.nasa.gov/image/PIA01667/PIA01667~orig.jpg"},
    "europa": {"image_url": "https://images-assets.nasa.gov/image/PIA00502/PIA00502~orig.jpg"},
    "ganymede": {"image_url": "https://images-assets.nasa.gov/image/PIA25721/PIA25721~small.jpg"},
    "callisto": {"image_url": "https://images-assets.nasa.gov/image/PIA00514/PIA00514~orig.jpg", "image_caption": "Galileo close-up of Callisto's surface."},
    "saturn": {"image_url": "https://images-assets.nasa.gov/image/PIA17172/PIA17172~orig.jpg", "image_caption": "Cassini mosaic of Saturn, its rings, moons, and Earth."},
    "titan": {"image_url": "https://images-assets.nasa.gov/image/PIA16177/PIA16177~small.jpg"},
    "enceladus": {"image_url": "https://images-assets.nasa.gov/image/PIA14858/PIA14858~small.jpg"},
    "rhea": {"image_url": "https://images-assets.nasa.gov/image/PIA02240/PIA02240~small.jpg"},
    "iapetus": {"image_url": "https://images-assets.nasa.gov/image/PIA12521/PIA12521~small.jpg"},
    "uranus": {"image_url": "https://images-assets.nasa.gov/image/PIA18182/PIA18182~orig.jpg"},
    "titania": {"image_url": "https://images-assets.nasa.gov/image/PIA00039/PIA00039~orig.jpg"},
    "oberon": {"image_url": "https://images-assets.nasa.gov/image/PIA00034/PIA00034~orig.jpg"},
    "miranda": {"image_url": "https://images-assets.nasa.gov/image/PIA00043/PIA00043~orig.jpg"},
    "neptune": {"image_url": "https://images-assets.nasa.gov/image/PIA01492/PIA01492~orig.jpg"},
    "triton": {"image_url": "https://images-assets.nasa.gov/image/PIA18668/PIA18668~small.jpg"},
    "proteus": {"image_url": None},
    "pluto": {"image_url": "https://images-assets.nasa.gov/image/PIA19693/PIA19693~small.jpg", "image_caption": "Near-true-color New Horizons views of Pluto and Charon."},
    "charon": {"image_url": "https://images-assets.nasa.gov/image/PIA19866/PIA19866~small.jpg"},
    "haumea": {"image_url": None},
    "makemake": {"image_url": None},
    "eris": {"image_url": None},
    "halley": {"image_url": "https://images-assets.nasa.gov/image/PIA17485/PIA17485~small.jpg", "image_caption": "Giotto close-up of Halley's comet nucleus."},
    "hale-bopp": {"image_url": "https://images-assets.nasa.gov/image/KSC-97pc558/KSC-97pc558~small.jpg"},
    "neowise": {"image_url": "https://images-assets.nasa.gov/image/NHQ202007120001/NHQ202007120001~small.jpg"},
}


SOLAR_SYSTEM_FACTS: Dict[str, Dict[str, Any]] = {
    "sun": {"diameter_m": 1_391_400_000, "distance_au": 0.0},
    "mercury": {"diameter_m": 4_879_400, "distance_au": 0.387},
    "venus": {"diameter_m": 12_103_600, "distance_au": 0.723},
    "earth": {"diameter_m": 12_742_000, "distance_au": 1.0},
    "moon": {"diameter_m": 3_474_800, "distance_au": 1.0, "parent_name": "Earth", "parent_orbit_km": 384_400},
    "mars": {"diameter_m": 6_779_000, "distance_au": 1.524},
    "phobos": {"diameter_m": 22_533, "distance_au": 1.524, "parent_name": "Mars", "parent_orbit_km": 9_376},
    "deimos": {"diameter_m": 12_400, "distance_au": 1.524, "parent_name": "Mars", "parent_orbit_km": 23_463},
    "ceres": {"diameter_m": 939_400, "distance_au": 2.77},
    "vesta": {"diameter_m": 525_400, "distance_au": 2.36},
    "pallas": {"diameter_m": 512_600, "distance_au": 2.77},
    "hygiea": {"diameter_m": 434_000, "distance_au": 3.14},
    "jupiter": {"diameter_m": 139_820_000, "distance_au": 5.204},
    "io": {"diameter_m": 3_643_200, "distance_au": 5.204, "parent_name": "Jupiter", "parent_orbit_km": 421_800},
    "europa": {"diameter_m": 3_121_600, "distance_au": 5.204, "parent_name": "Jupiter", "parent_orbit_km": 671_100},
    "ganymede": {"diameter_m": 5_268_200, "distance_au": 5.204, "parent_name": "Jupiter", "parent_orbit_km": 1_070_400},
    "callisto": {"diameter_m": 4_820_600, "distance_au": 5.204, "parent_name": "Jupiter", "parent_orbit_km": 1_882_700},
    "saturn": {"diameter_m": 116_460_000, "distance_au": 9.537},
    "titan": {"diameter_m": 5_149_500, "distance_au": 9.537, "parent_name": "Saturn", "parent_orbit_km": 1_221_870},
    "enceladus": {"diameter_m": 504_200, "distance_au": 9.537, "parent_name": "Saturn", "parent_orbit_km": 237_948},
    "rhea": {"diameter_m": 1_527_600, "distance_au": 9.537, "parent_name": "Saturn", "parent_orbit_km": 527_108},
    "iapetus": {"diameter_m": 1_469_000, "distance_au": 9.537, "parent_name": "Saturn", "parent_orbit_km": 3_560_820},
    "uranus": {"diameter_m": 50_724_000, "distance_au": 19.19},
    "titania": {"diameter_m": 1_576_800, "distance_au": 19.19, "parent_name": "Uranus", "parent_orbit_km": 435_910},
    "oberon": {"diameter_m": 1_522_800, "distance_au": 19.19, "parent_name": "Uranus", "parent_orbit_km": 583_520},
    "miranda": {"diameter_m": 471_600, "distance_au": 19.19, "parent_name": "Uranus", "parent_orbit_km": 129_900},
    "neptune": {"diameter_m": 49_244_000, "distance_au": 30.07},
    "triton": {"diameter_m": 2_706_800, "distance_au": 30.07, "parent_name": "Neptune", "parent_orbit_km": 354_800},
    "proteus": {"diameter_m": 420_000, "distance_au": 30.07, "parent_name": "Neptune", "parent_orbit_km": 117_647},
    "pluto": {"diameter_m": 2_376_600, "distance_au": 39.48},
    "charon": {"diameter_m": 1_212_000, "distance_au": 39.48, "parent_name": "Pluto", "parent_orbit_km": 19_596},
    "haumea": {"diameter_m": 1_595_000, "distance_au": 43.1},
    "makemake": {"diameter_m": 1_430_000, "distance_au": 45.4},
    "eris": {"diameter_m": 2_326_000, "distance_au": 67.7},
    "halley": {"diameter_m": 11_000, "distance_au": None},
    "hale-bopp": {"diameter_m": 60_000, "distance_au": None},
    "neowise": {"diameter_m": 5_000, "distance_au": None},
}

HABITABILITY_NOTES = {
    "sun": "Not habitable; the Sun is a star, not a solid world.",
    "earth": "Life is confirmed on Earth.",
    "mars": "No life has been detected; past habitability is under investigation.",
    "europa": "A subsurface ocean is suspected; no life has been detected.",
    "enceladus": "A subsurface ocean is present; no life has been detected.",
    "titan": "Complex organic chemistry is present; no life has been detected.",
}


def _normalize_space_object(obj: Dict[str, Any]) -> Dict[str, Any]:
    clean = dict(obj)
    clean.update(SOLAR_SYSTEM_FACTS.get(clean.get("id"), {}))
    clean.update(NASA_OBJECT_IMAGES.get(clean.get("id"), {}))
    coords = dict(clean.get("coordinates") or {"x": 0, "y": 0, "z": 0})
    clean["coordinates"] = {
        "x": float(coords.get("x", 0) or 0),
        "y": float(coords.get("y", 0) or 0),
        "z": float(coords.get("z", 0) or 0),
    }

    if "diameter_m" not in clean:
        clean["diameter_m"] = None
    clean.pop("life_probability", None)
    clean.pop("life_types", None)
    clean.pop("temperature_k", None)
    clean["habitability_note"] = HABITABILITY_NOTES.get(
        clean.get("id"), "No life has been detected; habitability is unknown."
    )
    return clean


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _format_nasa_objects(objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formatted: List[Dict[str, Any]] = []
    for index, obj in enumerate(objects):
        close_approach = obj.get("close_approach_data", [{}])[0]
        miss_distance = close_approach.get("miss_distance", {})
        estimated_diameter = obj.get("estimated_diameter", {}).get("meters", {})
        min_diameter = _safe_float(estimated_diameter.get("estimated_diameter_min", 0))
        max_diameter = _safe_float(estimated_diameter.get("estimated_diameter_max", 0))
        average_diameter = (min_diameter + max_diameter) / 2 if min_diameter and max_diameter else 0.0
        name = obj.get("name", "Unnamed asteroid")

        formatted.append(
            {
                "id": f"neo-{obj.get('id', index)}",
                "name": name,
                "type": "asteroid",
                "category": "Near-Earth object",
                "coordinates": {
                    "x": 260 + (index % 6) * 80,
                    "y": -180 + (index % 4) * 100,
                    "z": -260 + index * 70,
                },
                "close_approach_distance_au": _safe_float(miss_distance.get("astronomical", 0.0)),
                "description": "A near-Earth asteroid tracked by NASA's Jet Propulsion Laboratory for close approaches and orbital analysis.",
                "elements": ["Silicates", "Iron", "Nickel", "Carbon", "Magnesium"],
                "temperature_k": 180,
                "diameter_m": round(average_diameter, 2),
                "hazardous": bool(obj.get("is_potentially_hazardous_asteroid", False)),
            }
        )
    return formatted


def fetch_nasa_neo_feed(limit: int = 10) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    start_date = now.date().isoformat()
    end_date = (now + timedelta(days=7)).date().isoformat()

    try:
        response = requests.get(
            NASA_NEO_URL,
            params={"start_date": start_date, "end_date": end_date, "api_key": NASA_API_KEY},
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()
        near_earth_objects = payload.get("near_earth_objects", {})
        collected: List[Dict[str, Any]] = []
        for day_key in sorted(near_earth_objects.keys()):
            for item in near_earth_objects.get(day_key, []):
                collected.append(item)
                if len(collected) >= limit:
                    return _format_nasa_objects(collected)
        return _format_nasa_objects(collected)
    except requests.RequestException:
        return []


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/space")
def api_space() -> Any:
    objects = [_normalize_space_object(obj) for obj in EXPANDED_OBJECTS + fetch_nasa_neo_feed(limit=12)]
    return jsonify({
        "objects": objects,
        "source": "NASA",
        "catalog": "expanded_nasa_catalog",
        "api_key_set": NASA_API_KEY != "DEMO_KEY",
    })


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
