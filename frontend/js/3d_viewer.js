let scene, camera, renderer, controls, layoutGroup, activeCamera;
let dragControls = null;
let furnitureObjects = [];
let is2DMode = false;

// -------------------------------------------------------------
// Инициализация 3D сцены Three.js
// -------------------------------------------------------------
function init3DViewer(containerId) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error("Контейнер не найден:", containerId);
    return;
  }

  const width = container.clientWidth || window.innerWidth - 340;
  const height = container.clientHeight || window.innerHeight;

  // 1. Создание сцены
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x2f3640);

  // 2. Камера
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(15, 20, 25);

  // 3. Рендерер
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  container.innerHTML = "";
  container.appendChild(renderer.domElement);

  // 4. Управление OrbitControls
  if (typeof THREE.OrbitControls !== "undefined") {
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.01;
  }

  // 5. Освещение
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(20, 40, 20);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 2048;
  dirLight.shadow.mapSize.height = 2048;
  scene.add(dirLight);

  // 6. Сетка на земле (Grid)
  const gridHelper = new THREE.GridHelper(50, 50, 0x00d2d3, 0x57606f);
  gridHelper.position.y = -0.01;
  scene.add(gridHelper);

  layoutGroup = new THREE.Group();
  scene.add(layoutGroup);

  activeCamera = camera;

  window.addEventListener("resize", () => {
    const w = container.clientWidth || window.innerWidth - 340;
    const h = container.clientHeight || window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  function animate() {
    requestAnimationFrame(animate);
    if (controls) controls.update();
    renderer.render(scene, camera);
  }
  animate();

  // Дефолтный запуск
  update3DLayout({
    dimensions: { width: 12, length: 14, height: 2.8 },
    shape: "rectangle",
    rooms: {
      "Прихожая": { bounds: [0, 0, 5, 6], floor_type: "tile" },
      "Холл": { bounds: [5, 0, 9, 6], floor_type: "wood" },
      "Спальня": { bounds: [9, 0, 12, 6], floor_type: "wood" },
      "Зал": { bounds: [0, 6, 7, 14], floor_type: "wood" },
      "Кухня": { bounds: [7, 6, 10, 10], floor_type: "tile" },
      "Ванная": { bounds: [7, 10, 12, 14], floor_type: "tile" }
    }
  });
}

// -------------------------------------------------------------
// Вспомогательные функции отрисовки
// -------------------------------------------------------------

function createWall(x, y, z, w, h, d, material) {
  const geo = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  layoutGroup.add(mesh);
  return mesh;
}

// Детализированная 3D дверь с рамой и ручкой
function createDoor(x, y, z, width = 0.9, height = 2.1, rotationY = 0) {
  const doorGroup = new THREE.Group();

  // Коробка двери (рама)
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x3e2723, roughness: 0.5 });
  const frameGeo = new THREE.BoxGeometry(width + 0.08, height + 0.05, 0.16);
  const frame = new THREE.Mesh(frameGeo, frameMat);
  frame.position.set(0, height / 2, 0);
  doorGroup.add(frame);

  // Дверное полотно (контрастный цвет)
  const panelMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c, roughness: 0.4 });
  const panelGeo = new THREE.BoxGeometry(width * 0.92, height * 0.95, 0.06);
  const panel = new THREE.Mesh(panelGeo, panelMat);
  panel.position.set(0, height / 2, 0);
  doorGroup.add(panel);

  // Дверная ручка
  const handleMat = new THREE.MeshStandardMaterial({ color: 0xf1c40f, metalness: 0.8, roughness: 0.2 });
  const handleGeo = new THREE.SphereGeometry(0.05, 16, 16);
  const handle = new THREE.Mesh(handleGeo, handleMat);
  handle.position.set(width / 2 - 0.12, height / 2, 0.05);
  doorGroup.add(handle);

  doorGroup.position.set(x, y, z);
  doorGroup.rotation.y = rotationY;
  layoutGroup.add(doorGroup);
}

// Отрисовка труб (водопровод и канализация)
function createPipes(x, z, height) {
  const pipeGroup = new THREE.Group();

  // Холодная вода (синяя)
  const coldMat = new THREE.MeshStandardMaterial({ color: 0x2980b9, metalness: 0.4 });
  const coldGeo = new THREE.CylinderGeometry(0.03, 0.03, height, 16);
  const coldPipe = new THREE.Mesh(coldGeo, coldMat);
  coldPipe.position.set(x - 0.1, height / 2, z);
  pipeGroup.add(coldPipe);

  // Горячая вода (красная)
  const hotMat = new THREE.MeshStandardMaterial({ color: 0xc0392b, metalness: 0.4 });
  const hotGeo = new THREE.CylinderGeometry(0.03, 0.03, height, 16);
  const hotPipe = new THREE.Mesh(hotGeo, hotMat);
  hotPipe.position.set(x, height / 2, z);
  pipeGroup.add(hotPipe);

  // Канализационный стояк (серый)
  const drainMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.5 });
  const drainGeo = new THREE.CylinderGeometry(0.07, 0.07, height, 16);
  const drainPipe = new THREE.Mesh(drainGeo, drainMat);
  drainPipe.position.set(x + 0.12, height / 2, z);
  pipeGroup.add(drainPipe);

  layoutGroup.add(pipeGroup);
}

// Отрисовка линий кабели/электропроводка под потолком
function createCableRoute(x1, z1, x2, z2, y = 2.5) {
  const distance = Math.hypot(x2 - x1, z2 - z1);
  if (distance === 0) return;
  const angle = Math.atan2(z2 - z1, x2 - x1);

  const cableMat = new THREE.MeshBasicMaterial({ color: 0xf39c12 });
  const cableGeo = new THREE.CylinderGeometry(0.02, 0.02, distance, 8);
  const cable = new THREE.Mesh(cableGeo, cableMat);

  cable.position.set((x1 + x2) / 2, y, (z1 + z2) / 2);
  cable.rotation.y = -angle + Math.PI / 2;
  cable.rotation.z = Math.PI / 2;

  layoutGroup.add(cable);
}

function createRoomLabel(name, area, x, z) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = "rgba(47, 54, 64, 0.85)";
  ctx.fillRect(0, 0, 256, 128);
  ctx.strokeStyle = "#00d2d3";
  ctx.lineWidth = 4;
  ctx.strokeRect(2, 2, 252, 124);

  ctx.fillStyle = "#ffffff";
  ctx.font = "Bold 22px Arial";
  ctx.textAlign = "center";
  ctx.fillText(name, 128, 50);

  ctx.fillStyle = "#00d2d3";
  ctx.font = "18px Arial";
  ctx.fillText(`${area.toFixed(1)} m²`, 128, 90);

  const texture = new THREE.CanvasTexture(canvas);
  const spriteMat = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(spriteMat);
  sprite.position.set(x, 0.3, z);
  sprite.scale.set(3, 1.5, 1);
  layoutGroup.add(sprite);
}

// -------------------------------------------------------------
// Основная генерация 3D сцены
// -------------------------------------------------------------
function update3DLayout(layoutData) {
  if (!layoutGroup) return;

  if (dragControls) {
    dragControls.dispose();
    dragControls = null;
  }
  furnitureObjects = [];

  while (layoutGroup.children.length > 0) {
    layoutGroup.remove(layoutGroup.children[0]);
  }

  if (!layoutData) layoutData = {};
  const dim = layoutData.dimensions || { width: 12, length: 14, height: 2.8 };
  const rooms = layoutData.rooms || {};
  const rawShape = layoutData.shape || "rectangle";
  const shape = String(rawShape).toLowerCase().trim();

  const wallMat = new THREE.MeshStandardMaterial({ color: 0xbdc3c7, roughness: 0.6 });
  const intWallMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.6 });
  const wallHeight = dim.height || 2.8;

  const roomKeys = Object.keys(rooms);

  roomKeys.forEach((rName) => {
    const room = rooms[rName];
    if (!room || !room.bounds) return;
    const [x1, y1, x2, y2] = room.bounds;
    const rw = x2 - x1;
    const rl = y2 - y1;
    const area = rw * rl;

    // Пол комнаты
    const floorGeo = new THREE.PlaneGeometry(rw, rl);
    const floorMat = new THREE.MeshStandardMaterial({
      color: room.floor_type === "wood" ? 0xd2b48c : 0x95a5a6,
      side: THREE.DoubleSide
    });

    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.position.set(x1 + rw / 2, 0.01, y1 + rl / 2);
    floorMesh.receiveShadow = true;
    layoutGroup.add(floorMesh);

    // Внутренние перегородки
    createWall(x1 + rw / 2, wallHeight / 2, y1, rw, wallHeight, 0.15, intWallMat);
    createWall(x1 + rw / 2, wallHeight / 2, y2, rw, wallHeight, 0.15, intWallMat);
    createWall(x1, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
    createWall(x2, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);

    // Двери (если есть в объекте от бэкенда, либо авто-создание для каждой комнаты)
    if (room.doors && Array.isArray(room.doors) && room.doors.length > 0) {
      room.doors.forEach((door) => {
        const dWidth = door.width || 0.9;
        if (door.wall === "north") createDoor(x1 + rw * door.pos, 0, y1, dWidth, 2.1, 0);
        else if (door.wall === "south") createDoor(x1 + rw * door.pos, 0, y2, dWidth, 2.1, 0);
        else if (door.wall === "west") createDoor(x1, 0, y1 + rl * door.pos, dWidth, 2.1, Math.PI / 2);
        else if (door.wall === "east") createDoor(x2, 0, y1 + rl * door.pos, dWidth, 2.1, Math.PI / 2);
      });
    } else {
      // Фолбэк: Автоматическая дверь в южной стене комнаты
      createDoor(x1 + rw / 2, 0, y2, 0.9, 2.1, 0);
    }

    // Отрисовка коммуникаций (трубы) в мокрых зонах (Кухня, Ванная, Санузел)
    const lowerName = rName.toLowerCase();
    if (lowerName.includes("ванн") || lowerName.includes("санузел") || lowerName.includes("кухн") || lowerName.includes("туалет")) {
      createPipes(x1 + 0.4, y1 + 0.4, wallHeight);
    }

    // Отрисовка трассы электропроводки по периметру каждой комнаты
    createCableRoute(x1, y1, x2, y1, 2.5);
    createCableRoute(x1, y1, x1, y2, 2.5);

    // Табличка с названием комнаты
    createRoomLabel(rName, area, x1 + rw / 2, y1 + rl / 2);
  });

  // Входная дверь в дом (на фасадной стене)
  createDoor(dim.width / 2, 0, dim.length, 1.0, 2.2, 0);

  // Внешний контур стен
  const w = dim.width;
  const l = dim.length;

  if (shape === "circle" || shape === "ellipse" || shape === "круг" || shape === "эллипс") {
    const rx = w / 2;
    const ry = l / 2;
    const cylGeo = new THREE.CylinderGeometry(rx, rx, wallHeight, 32, 1, true);
    const cylMesh = new THREE.Mesh(cylGeo, wallMat);
    cylMesh.position.set(rx, wallHeight / 2, ry);
    if (shape === "ellipse" || shape === "эллипс") cylMesh.scale.set(1, 1, ry / rx);
    layoutGroup.add(cylMesh);
  } else {
    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);
    createWall(w / 2, wallHeight / 2, l - 0.19, w, wallHeight, 0.38, wallMat);
    createWall(0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
    createWall(w - 0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
  }

  if (controls) {
    controls.target.set(w / 2, 0, l / 2);
  }
}

function toggleViewMode(to2D) {
  is2DMode = to2D;
  if (!camera) return;
  if (to2D) {
    camera.position.set(12, 35, 14.01);
    if (controls) {
      controls.target.set(12, 0, 14);
      controls.enableRotate = false;
    }
  } else {
    camera.position.set(15, 20, 25);
    if (controls) {
      controls.enableRotate = true;
    }
  }
}