const mapEl = document.getElementById("space-map");
const detailPanel = document.getElementById("object-detail");
const zoomInBtn = document.getElementById("zoom-in");
const zoomOutBtn = document.getElementById("zoom-out");

const state = {
  objects: [],
  selectedId: null,
  zoom: 1,
  yaw: 0.7,
  pitch: -0.35,
  dragging: false,
  lastX: 0,
  lastY: 0,
};

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function getTypeColor(type) {
  const palette = {
    star: "#ffd166",
    planet: "#7bdff2",
    moon: "#b8c0ff",
    asteroid: "#f4a261",
    comet: "#c7f9cc",
    exoplanet: "#90e0ef",
    dwarf_planet: "#a8dadc",
  };
  return palette[type] || "#dfe6f3";
}

function getObjectColors(object) {
  const surfaces = {
    Sun: ["#fff2ae", "#f6a623", "#6e260b"],
    Mercury: ["#ddd8d0", "#8d8985", "#292a2d"],
    Venus: ["#fff0b8", "#d69a51", "#59331f"],
    Earth: ["#b7f1ff", "#2479bb", "#071d43"],
    Moon: ["#f4f1e9", "#99958e", "#292b31"],
    Mars: ["#ffd0a2", "#c34b2d", "#401b1a"],
    Jupiter: ["#fff0c8", "#c88b58", "#452b27"],
    Saturn: ["#fff1c4", "#c3a16c", "#453426"],
    Uranus: ["#d4ffff", "#64bdc5", "#153f56"],
    Neptune: ["#a9d5ff", "#315cdb", "#101c62"],
  };
  if (surfaces[object.name]) return surfaces[object.name];

  const fallback = {
    star: ["#fff2ae", "#f6a623", "#6e260b"],
    planet: ["#c7f4ff", "#438cc4", "#142c50"],
    moon: ["#f2f0e8", "#a1a2a4", "#30333a"],
    asteroid: ["#ffe0bd", "#a97c5b", "#342820"],
    comet: ["#ffffff", "#596a73", "#111820"],
    exoplanet: ["#d4f7ff", "#5395bd", "#193654"],
    dwarf_planet: ["#f4e5c9", "#a88e6c", "#352f2a"],
  };
  return fallback[object.type] || ["#ecf5ff", getTypeColor(object.type), "#1b2638"];
}

function addSurfaceDetails(group, object, x, y, radius, clipId) {
  const scale = radius / 50;
  const surface = document.createElementNS("http://www.w3.org/2000/svg", "g");
  surface.setAttribute("transform", `translate(${x - radius} ${y - radius}) scale(${scale})`);

  const clipped = document.createElementNS("http://www.w3.org/2000/svg", "g");
  clipped.setAttribute("clip-path", `url(#${clipId})`);
  surface.appendChild(clipped);
  group.appendChild(surface);

  const addShape = (tag, attributes) => {
    const shape = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attributes).forEach(([name, value]) => shape.setAttribute(name, value));
    clipped.appendChild(shape);
  };

  if (object.type === "comet") {
    addShape("path", { d: "M34 43 L39 34 48 31 56 35 63 32 69 40 67 49 73 56 67 64 58 66 52 73 43 68 36 70 31 62 33 54 28 49Z", fill: "#29343d", opacity: "0.8" });
    addShape("path", { d: "M37 43 L42 37 50 35 55 39 62 37", fill: "none", stroke: "#cce8ef", "stroke-width": "2", opacity: "0.48" });
    addShape("circle", { cx: "58", cy: "55", r: "4", fill: "#d9f3f7", opacity: "0.3" });
  } else if (object.name === "Earth") {
    addShape("path", { d: "M13 31 L21 25 27 27 32 23 39 26 43 32 39 37 43 42 37 47 34 55 29 58 26 51 21 48 20 41 15 38Z", fill: "#82a66a", opacity: "0.92" });
    addShape("path", { d: "M46 58 L53 55 60 59 63 66 60 73 57 83 52 79 50 71 46 67Z", fill: "#9a9b65", opacity: "0.92" });
    addShape("path", { d: "M61 29 L68 25 76 27 80 33 76 38 71 39 69 46 64 43 62 37Z", fill: "#92a76c", opacity: "0.9" });
    addShape("path", { d: "M5 46 C25 41 34 49 48 45 S76 42 96 47", fill: "none", stroke: "#e5f5ed", "stroke-width": "2", opacity: "0.4" });
  } else if (["Jupiter", "Saturn", "Uranus", "Neptune"].includes(object.name)) {
    const bands = object.name === "Jupiter"
      ? [[22, "#f3d5a6"], [35, "#8f5940"], [48, "#e6c394"], [62, "#9d6041"], [77, "#e7c79b"]]
      : [[24, "#f2dcae"], [39, "#a98556"], [54, "#ead5a5"], [68, "#9c7851"], [80, "#e7cf9e"]];
    bands.forEach(([bandY, color], index) => {
      const top = Number(bandY);
      addShape("path", {
        d: `M-5 ${top} C20 ${top - 7} 35 ${top + 8} 55 ${top} S85 ${top - 6} 105 ${top + 2} L105 ${top + 9} C80 ${top + 3} 67 ${top + 15} 48 ${top + 8} S18 ${top + 5} -5 ${top + 12}Z`,
        fill: color,
        opacity: index % 2 === 0 ? "0.55" : "0.72",
      });
    });
    if (object.name === "Jupiter") {
      addShape("ellipse", { cx: "70", cy: "62", rx: "9", ry: "4", fill: "#b45b42", opacity: "0.88" });
    }
  } else if (object.name === "Mars") {
    addShape("path", { d: "M17 38 C24 30 31 35 36 40 L33 48 25 51 19 47Z", fill: "#e98157", opacity: "0.62" });
    addShape("path", { d: "M59 56 C67 47 77 51 80 59 L74 65 78 72 68 76 63 68Z", fill: "#e98157", opacity: "0.54" });
    addShape("ellipse", { cx: "50", cy: "8", rx: "20", ry: "5", fill: "#f5e5d0", opacity: "0.75" });
  } else if (object.type === "star") {
    [[27, 38, 11], [69, 33, 8], [58, 69, 13], [33, 73, 7]].forEach(([spotX, spotY, size]) => {
      addShape("circle", { cx: spotX, cy: spotY, r: size, fill: "#ffb347", opacity: "0.42" });
    });
    addShape("path", { d: "M8 57 C27 44 37 51 51 44 S77 42 94 35", fill: "none", stroke: "#fff0b5", "stroke-width": "3", opacity: "0.35" });
  } else {
    [[29, 35, 8], [65, 28, 5], [57, 59, 10], [34, 72, 5], [78, 69, 4]].forEach(([craterX, craterY, size]) => {
      addShape("circle", { cx: craterX, cy: craterY, r: size, fill: "#17191d", opacity: "0.22" });
      addShape("circle", { cx: Number(craterX) - 1.5, cy: Number(craterY) - 1.5, r: Number(size) * 0.62, fill: "#ffffff", opacity: "0.12" });
    });
  }
}

function getObjectRadius(object) {
  const diameter = Number(object.diameter_m || 0);

  const defaults = {
    star: 14,
    planet: 8,
    moon: 5,
    dwarf_planet: 6,
    asteroid: 3,
    comet: 4,
    exoplanet: 6,
  };

  if (diameter > 0) return Math.max(defaults[object.type] || 4, Math.sqrt(diameter) / 1200);
  return defaults[object.type] || 4;
}

function projectPoint(object) {
  const { x, y, z } = object.coordinates || { x: 0, y: 0, z: 0 };

  const cosY = Math.cos(state.yaw);
  const sinY = Math.sin(state.yaw);
  const x1 = x * cosY - z * sinY;
  const z1 = x * sinY + z * cosY;

  const cosX = Math.cos(state.pitch);
  const sinX = Math.sin(state.pitch);
  const y1 = y * cosX - z1 * sinX;
  const z2 = y * sinX + z1 * cosX;

  const perspective = 900 / (900 + z2);
  const scale = state.zoom * perspective;
  const screenX = window.innerWidth / 2 + x1 * scale;
  const screenY = window.innerHeight / 2 + y1 * scale;

  return {
    x: screenX,
    y: screenY,
    scale,
    z: z2,
    visible: z2 > -900,
  };
}

function renderBackgroundStars() {
  const starLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
  for (let i = 0; i < 180; i += 1) {
    const cx = Math.random() * window.innerWidth;
    const cy = Math.random() * window.innerHeight;
    const r = Math.random() * 2.1 + 0.8;

    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot.setAttribute("cx", cx);
    dot.setAttribute("cy", cy);
    dot.setAttribute("r", r);
    dot.setAttribute("fill", "rgba(255,255,255,0.8)");
    starLayer.appendChild(dot);
  }
  return starLayer;
}

function renderAsteroidBelt() {
  const belt = document.createElementNS("http://www.w3.org/2000/svg", "g");
  belt.setAttribute("class", "asteroid-belt");
  belt.setAttribute("pointer-events", "none");
  const centerX = window.innerWidth / 2;
  const centerY = window.innerHeight / 2;

  [[188, 76], [228, 94], [270, 112]].forEach(([rx, ry], index) => {
    const orbit = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
    orbit.setAttribute("cx", centerX);
    orbit.setAttribute("cy", centerY);
    orbit.setAttribute("rx", rx * state.zoom);
    orbit.setAttribute("ry", ry * state.zoom);
    orbit.setAttribute("fill", "none");
    orbit.setAttribute("stroke", index === 1 ? "rgba(225, 184, 135, 0.2)" : "rgba(190, 157, 122, 0.1)");
    orbit.setAttribute("stroke-width", "1");
    belt.appendChild(orbit);
  });

  for (let index = 0; index < 320; index += 1) {
    const angle = index * 2.399963229728653;
    const noise = (Math.sin(index * 127.1 + 311.7) * 43758.5453) % 1;
    const radius = (190 + (noise + 1) * 0.5 * 78) * state.zoom;
    const x = centerX + Math.cos(angle) * radius;
    const y = centerY + Math.sin(angle) * radius * 0.42;
    const particle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    particle.setAttribute("cx", x);
    particle.setAttribute("cy", y);
    particle.setAttribute("r", `${(0.45 + ((index * 37) % 100) / 100) * state.zoom}`);
    particle.setAttribute("fill", index % 4 === 0 ? "#e6c39e" : "#ab9074");
    particle.setAttribute("opacity", `${0.16 + ((index * 19) % 60) / 100}`);
    belt.appendChild(particle);
  }

  const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
  label.setAttribute("x", centerX + 180 * state.zoom);
  label.setAttribute("y", centerY + 78 * state.zoom);
  label.setAttribute("fill", "rgba(225, 195, 163, 0.58)");
  label.setAttribute("font-size", "9");
  label.setAttribute("font-family", "IBM Plex Mono, monospace");
  label.textContent = "MAIN ASTEROID BELT";
  belt.appendChild(label);
  return belt;
}

function addCometTail(group, object, x, y, radius, gradientId) {
  const directionX = x - window.innerWidth / 2;
  const directionY = y - window.innerHeight / 2;
  const directionLength = Math.hypot(directionX, directionY) || 1;
  const unitX = directionX / directionLength;
  const unitY = directionY / directionLength;
  const normalX = -unitY;
  const normalY = unitX;
  const tailLength = Math.max(75, radius * 13);
  const tipX = x + unitX * tailLength;
  const tipY = y + unitY * tailLength;
  const tail = document.createElementNS("http://www.w3.org/2000/svg", "g");
  tail.setAttribute("pointer-events", "none");

  const dustGradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
  dustGradient.setAttribute("id", gradientId);
  dustGradient.setAttribute("gradientUnits", "userSpaceOnUse");
  dustGradient.setAttribute("x1", x);
  dustGradient.setAttribute("y1", y);
  dustGradient.setAttribute("x2", tipX);
  dustGradient.setAttribute("y2", tipY);
  [["0%", "#fff6d7", "0.92"], ["35%", "#ffd89a", "0.58"], ["100%", "#ffc16e", "0"]].forEach(([offset, color, opacity]) => {
    const stop = document.createElementNS("http://www.w3.org/2000/svg", "stop");
    stop.setAttribute("offset", offset);
    stop.setAttribute("stop-color", color);
    stop.setAttribute("stop-opacity", opacity);
    dustGradient.appendChild(stop);
  });
  group.querySelector("defs").appendChild(dustGradient);

  const dustTail = document.createElementNS("http://www.w3.org/2000/svg", "path");
  dustTail.setAttribute("d", `M${x + normalX * radius} ${y + normalY * radius} C${x + unitX * tailLength * 0.3 + normalX * radius * 3} ${y + unitY * tailLength * 0.3 + normalY * radius * 3} ${tipX + normalX * radius * 0.55} ${tipY + normalY * radius * 0.55} ${tipX} ${tipY} C${tipX - normalX * radius * 0.55} ${tipY - normalY * radius * 0.55} ${x + unitX * tailLength * 0.24 - normalX * radius * 1.5} ${y + unitY * tailLength * 0.24 - normalY * radius * 1.5} ${x - normalX * radius} ${y - normalY * radius}Z`);
  dustTail.setAttribute("fill", `url(#${gradientId})`);
  tail.appendChild(dustTail);

  const ionTail = document.createElementNS("http://www.w3.org/2000/svg", "path");
  ionTail.setAttribute("d", `M${x + normalX * radius * 0.28} ${y + normalY * radius * 0.28} Q${x + unitX * tailLength * 0.55 + normalX * radius} ${y + unitY * tailLength * 0.55 + normalY * radius} ${tipX} ${tipY} Q${x + unitX * tailLength * 0.42 - normalX * radius} ${y + unitY * tailLength * 0.42 - normalY * radius} ${x - normalX * radius * 0.28} ${y - normalY * radius * 0.28}Z`);
  ionTail.setAttribute("fill", "rgba(122, 220, 255, 0.22)");
  tail.appendChild(ionTail);

  const coma = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  coma.setAttribute("cx", x);
  coma.setAttribute("cy", y);
  coma.setAttribute("r", Math.max(8, radius * 2.7));
  coma.setAttribute("fill", "#fff2cb");
  coma.setAttribute("opacity", "0.44");
  tail.appendChild(coma);
  group.appendChild(tail);
}

function selectObject(object) {
  if (!object) return;
  state.selectedId = object.id;
  renderMap();
  renderDetail(object);
}

function renderDetail(object) {
  if (!object) return;

  const coordinates = object.coordinates
    ? `${object.coordinates.x}, ${object.coordinates.y}, ${object.coordinates.z}`
    : "Unassigned";

  const distance = object.distance_au !== undefined && object.distance_au !== null
    ? `${Number(object.distance_au).toFixed(3)} AU`
    : "Unknown";
  const parentOrbit = object.parent_orbit_km
    ? `${Number(object.parent_orbit_km).toLocaleString("en-US")} km`
    : null;
  const closeApproach = object.close_approach_distance_au !== undefined
    ? `${Number(object.close_approach_distance_au).toFixed(4)} AU`
    : null;
  const hazardFact = object.hazardous !== undefined
    ? `<li>• HAZARD: ${object.hazardous ? "Potentially hazardous" : "Not flagged as hazardous"}</li>`
    : "";
  const diameterMeters = Number(object.diameter_m || 0);
  const diameter = diameterMeters >= 1_000_000
    ? `${(diameterMeters / 1000).toLocaleString("en-US", { maximumFractionDigits: 0 })} km`
    : diameterMeters >= 1000
      ? `${(diameterMeters / 1000).toLocaleString("en-US", { maximumFractionDigits: 2 })} km`
      : diameterMeters > 0
        ? `${diameterMeters.toLocaleString("en-US", { maximumFractionDigits: 0 })} m`
        : "Unknown";

  detailPanel.classList.remove("hidden");
  detailPanel.innerHTML = `
    <div class="detail-header">
      <div>
        <div class="eyebrow">${object.type}</div>
        <h2>${object.name}</h2>
      </div>
      <button class="close-button" aria-label="Close details">×</button>
    </div>

    ${object.image_url ? `<img class="detail-image" src="${object.image_url}" alt="${object.name}" />` : ""}
    ${object.image_caption ? `<p class="image-caption">${object.image_caption}</p>` : ""}

    <div class="detail-body">
      <p class="category">${object.category}</p>
      <p class="summary">${object.description}</p>

      <ul class="facts">
        <li>• OBJECT: ${object.name}</li>
        <li>• TYPE: ${object.type}</li>
        <li>• MAP POSITION: ${coordinates}</li>
        <li>• ORBIT FROM SUN: ${distance}</li>
        ${parentOrbit ? `<li>• ORBIT AROUND ${object.parent_name.toUpperCase()}: ${parentOrbit}</li>` : ""}
        ${closeApproach ? `<li>• CLOSE APPROACH FROM EARTH: ${closeApproach}</li>` : ""}
        <li>• DIAMETER: ${diameter}</li>
        <li>• COMPOSITION: ${(object.elements || []).slice(0, 5).join(", ") || "Unknown"}</li>
        ${hazardFact}
        <li>• HABITABILITY: ${object.habitability_note || "No life has been detected; habitability is unknown."}</li>
      </ul>
    </div>
  `;

  detailPanel.querySelector(".close-button").addEventListener("click", () => {
    detailPanel.classList.add("hidden");
  });
}

function renderMap() {
  mapEl.innerHTML = "";
  mapEl.appendChild(renderBackgroundStars());
  mapEl.appendChild(renderAsteroidBelt());

  state.objects.forEach((object) => {
    const projected = projectPoint(object);
    if (!projected.visible) return;

    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", "space-object");
    group.style.cursor = "pointer";

    const radius = getObjectRadius(object) * projected.scale;
    const objectKey = String(object.id).replace(/[^a-zA-Z0-9_-]/g, "-");
    const surfaceId = `surface-${objectKey}`;
    const lightingId = `lighting-${objectKey}`;
    const clipId = `clip-${objectKey}`;
    const [highlightColor, surfaceColor, shadowColor] = getObjectColors(object);

    const definitions = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    const surfaceGradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
    surfaceGradient.setAttribute("id", surfaceId);
    surfaceGradient.setAttribute("cx", "30%");
    surfaceGradient.setAttribute("cy", "25%");
    surfaceGradient.setAttribute("r", "78%");
    [["0%", highlightColor], ["54%", surfaceColor], ["100%", shadowColor]].forEach(([offset, color]) => {
      const stop = document.createElementNS("http://www.w3.org/2000/svg", "stop");
      stop.setAttribute("offset", offset);
      stop.setAttribute("stop-color", color);
      surfaceGradient.appendChild(stop);
    });

    const lightingGradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
    lightingGradient.setAttribute("id", lightingId);
    lightingGradient.setAttribute("cx", "27%");
    lightingGradient.setAttribute("cy", "22%");
    lightingGradient.setAttribute("r", "78%");
    [["0%", "#ffffff", "0.2"], ["48%", "#ffffff", "0"], ["78%", "#000000", "0.08"], ["100%", "#000000", "0.68"]].forEach(([offset, color, opacity]) => {
      const stop = document.createElementNS("http://www.w3.org/2000/svg", "stop");
      stop.setAttribute("offset", offset);
      stop.setAttribute("stop-color", color);
      stop.setAttribute("stop-opacity", opacity);
      lightingGradient.appendChild(stop);
    });

    const clipPath = document.createElementNS("http://www.w3.org/2000/svg", "clipPath");
    clipPath.setAttribute("id", clipId);
    clipPath.setAttribute("clipPathUnits", "userSpaceOnUse");
    const clipCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    clipCircle.setAttribute("cx", "50");
    clipCircle.setAttribute("cy", "50");
    clipCircle.setAttribute("r", "50");
    clipPath.appendChild(clipCircle);
    definitions.append(surfaceGradient, lightingGradient, clipPath);
    group.appendChild(definitions);

    if (object.type === "comet") {
      addCometTail(group, object, projected.x, projected.y, radius, `comet-tail-${objectKey}`);
    }

    if (object.type === "planet" && object.name === "Saturn") {
      const ring = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
      ring.setAttribute("cx", projected.x);
      ring.setAttribute("cy", projected.y);
      ring.setAttribute("rx", radius * 2.1);
      ring.setAttribute("ry", radius * 0.72);
      ring.setAttribute("fill", "none");
      ring.setAttribute("stroke", "rgba(210, 180, 140, 0.7)");
      ring.setAttribute("stroke-width", "1.5");
      group.appendChild(ring);
    }

    const glow = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    glow.setAttribute("cx", projected.x);
    glow.setAttribute("cy", projected.y);
    glow.setAttribute("r", radius * 2.2);
    glow.setAttribute("fill", surfaceColor);
    glow.setAttribute("opacity", object.type === "star" ? "0.2" : "0.09");
    group.appendChild(glow);

    const sphere = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    sphere.setAttribute("cx", projected.x);
    sphere.setAttribute("cy", projected.y);
    sphere.setAttribute("r", radius);
    sphere.setAttribute("fill", `url(#${surfaceId})`);
    sphere.setAttribute("stroke", "rgba(255,255,255,0.48)");
    sphere.setAttribute("stroke-width", "0.8");
    group.appendChild(sphere);

    addSurfaceDetails(group, object, projected.x, projected.y, radius, clipId);

    const lighting = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    lighting.setAttribute("cx", projected.x);
    lighting.setAttribute("cy", projected.y);
    lighting.setAttribute("r", radius);
    lighting.setAttribute("fill", `url(#${lightingId})`);
    lighting.setAttribute("pointer-events", "none");
    group.appendChild(lighting);

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", projected.x + radius + 8);
    label.setAttribute("y", projected.y - radius - 8);
    label.setAttribute("fill", "rgba(255,255,255,0.85)");
    label.setAttribute("font-size", `${11 * projected.scale}px`);
    label.setAttribute("font-family", "IBM Plex Mono, monospace");
    label.textContent = object.name;
    group.appendChild(label);

    group.addEventListener("pointerdown", (event) => {
      event.stopPropagation();
      state.dragging = false;
      selectObject(object);
    });

    group.addEventListener("click", (event) => {
      event.stopPropagation();
      selectObject(object);
    });

    mapEl.appendChild(group);
  });
}

function syncWithSelectedDefault() {
  if (!state.objects.length) return;
  const current = state.objects.find((obj) => obj.id === state.selectedId) || state.objects[0];
  renderDetail(current);
}

fetch("/api/space")
  .then((response) => response.json())
  .then((payload) => {
    state.objects = payload.objects || [];
    state.selectedId = state.objects[0]?.id || null;
    renderMap();
    syncWithSelectedDefault();
  })
  .catch((error) => {
    console.error(error);
    detailPanel.classList.remove("hidden");
    detailPanel.innerHTML = `
      <div class="detail-header">
        <div>
          <div class="eyebrow">SYSTEM</div>
          <h2>NASA FEED ERROR</h2>
        </div>
      </div>
      <div class="detail-body">
        <p class="summary">Unable to load the live NASA dataset. Please confirm your API key is set in the environment.</p>
      </div>
    `;
  });

mapEl.addEventListener("pointerdown", (event) => {
  if (event.target && event.target.closest && event.target.closest(".space-object")) {
    return;
  }

  state.dragging = true;
  state.lastX = event.clientX;
  state.lastY = event.clientY;
  mapEl.setPointerCapture(event.pointerId);
});

mapEl.addEventListener("pointermove", (event) => {
  if (!state.dragging) return;
  const dx = event.clientX - state.lastX;
  const dy = event.clientY - state.lastY;
  state.lastX = event.clientX;
  state.lastY = event.clientY;
  state.yaw += dx * 0.008;
  state.pitch = clamp(state.pitch + dy * 0.008, -1.4, 1.4);
  renderMap();
});

mapEl.addEventListener("pointerup", () => {
  state.dragging = false;
});

mapEl.addEventListener("pointerleave", () => {
  state.dragging = false;
});

mapEl.addEventListener("wheel", (event) => {
  event.preventDefault();
  const delta = event.deltaY < 0 ? 0.14 : -0.14;
  state.zoom = clamp(state.zoom + delta, 0.5, 2.8);
  renderMap();
}, { passive: false });

zoomInBtn.addEventListener("click", () => {
  state.zoom = clamp(state.zoom + 0.18, 0.5, 2.8);
  renderMap();
});

zoomOutBtn.addEventListener("click", () => {
  state.zoom = clamp(state.zoom - 0.18, 0.5, 2.8);
  renderMap();
});

detailPanel.addEventListener("click", (event) => {
  event.stopPropagation();
});

window.addEventListener("resize", renderMap);
