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

  // Очистка контейнера перед добавлением
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

  // Группа для всех динамических элементов дома
  layoutGroup = new THREE.Group();
  scene.add(layoutGroup);

  activeCamera = camera;

  // Обработка изменения размера окна
  window.addEventListener("resize", () => {
    const w = container.clientWidth || window.innerWidth - 340;
    const h = container.clientHeight || window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  // Цикл анимации
  function animate() {
    requestAnimationFrame(animate);
    if (controls) controls.update();
    renderer.render(scene, camera);
  }
  animate();

  // Отрисуем дефолтный прямоугольник при запуске
  update3DLayout({
    dimensions: { width: 12, length: 14, height: 2.8 },
    shape: "rectangle",
    rooms: {
      "Гостиная": { bounds: [0, 0, 7, 8], floor_type: "wood" },
      "Спальня": { bounds: [7, 0, 12, 8], floor_type: "tile" },
      "Кухня": { bounds: [0, 8, 6, 14], floor_type: "tile" },
      "Санузел": { bounds: [6, 8, 12, 14], floor_type: "tile" }
    }
  });
}

// Вспомогательные функции отрисовки
function createWall(x, y, z, w, h, d, material) {
  const geo = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  layoutGroup.add(mesh);
  return mesh;
}

function createDoor(x, y, z, w, h, rotationY) {
  const doorGeo = new THREE.BoxGeometry(w, h, 0.08);
  const doorMat = new THREE.MeshStandardMaterial({ color: 0x8e44ad });
  const doorMesh = new THREE.Mesh(doorGeo, doorMat);
  doorMesh.position.set(x, y + h / 2, z);
  doorMesh.rotation.y = rotationY;
  layoutGroup.add(doorMesh);
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
  const furniture = layoutData.furniture || [];

  const rawShape = layoutData.shape || "rectangle";
  const shape = String(rawShape).toLowerCase().trim();

  const wallMat = new THREE.MeshStandardMaterial({ color: 0xbdc3c7, roughness: 0.6 });
  const intWallMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.6 });
  const wallHeight = dim.height || 2.8;

  // 1. Отрисовка комнат
  const roomKeys = Object.keys(rooms);
  if (roomKeys.length === 0) {
    // Резервная отрисовка единого пола, если бэкенд не прислал комнаты
    const floorGeo = new THREE.PlaneGeometry(dim.width, dim.length);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x34495e, side: THREE.DoubleSide });
    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.position.set(dim.width / 2, 0.01, dim.length / 2);
    layoutGroup.add(floorMesh);
  } else {
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

      // Перегородки
      createWall(x1 + rw / 2, wallHeight / 2, y1, rw, wallHeight, 0.15, intWallMat);
      createWall(x1 + rw / 2, wallHeight / 2, y2, rw, wallHeight, 0.15, intWallMat);
      createWall(x1, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
      createWall(x2, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);

      // Двери
      if (room.doors && Array.isArray(room.doors)) {
        room.doors.forEach((door) => {
          const dWidth = door.width || 0.8;
          if (door.wall === "north") createDoor(x1 + rw * door.pos, 0, y1, dWidth, 2.1, 0);
          else if (door.wall === "south") createDoor(x1 + rw * door.pos, 0, y2, dWidth, 2.1, 0);
          else if (door.wall === "west") createDoor(x1, 0, y1 + rl * door.pos, dWidth, 2.1, Math.PI / 2);
          else if (door.wall === "east") createDoor(x2, 0, y1 + rl * door.pos, dWidth, 2.1, Math.PI / 2);
        });
      }

      // Табличка
      createRoomLabel(rName, area, x1 + rw / 2, y1 + rl / 2);
    });
  }

  // 2. Внешний контур стен
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
  } else if (shape === "l_shape" || shape === "г-образный" || shape === "l-образный") {
    const cutW = w * 0.4;
    const cutL = l * 0.4;
    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);
    createWall(0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
    createWall((w - cutW) / 2, wallHeight / 2, l - 0.19, w - cutW, wallHeight, 0.38, wallMat);
    createWall(w - cutW, wallHeight / 2, l - cutL / 2, 0.38, wallHeight, cutL, wallMat);
    createWall(w - cutW / 2, wallHeight / 2, l - cutL, cutW, wallHeight, 0.38, wallMat);
    createWall(w - 0.19, wallHeight / 2, (l - cutL) / 2, 0.38, wallHeight, l - cutL, wallMat);
  } else if (shape === "t_shape" || shape === "т-образный") {
    const wingW = w * 0.3;
    const wingL = l * 0.4;
    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);
    createWall(0.19, wallHeight / 2, wingL / 2, 0.38, wallHeight, wingL, wallMat);
    createWall(w - 0.19, wallHeight / 2, wingL / 2, 0.38, wallHeight, wingL, wallMat);
    createWall(wingW / 2, wallHeight / 2, wingL, wingW, wallHeight, 0.38, wallMat);
    createWall(w - wingW / 2, wallHeight / 2, wingL, wingW, wallHeight, 0.38, wallMat);
    createWall(wingW + 0.19, wallHeight / 2, wingL + (l - wingL) / 2, 0.38, wallHeight, l - wingL, wallMat);
    createWall(w - wingW - 0.19, wallHeight / 2, wingL + (l - wingL) / 2, 0.38, wallHeight, l - wingL, wallMat);
    createWall(w / 2, wallHeight / 2, l - 0.19, w - wingW * 2, wallHeight, 0.38, wallMat);
  } else {
    // Прямоугольник по умолчанию
    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);
    createWall(w / 2, wallHeight / 2, l - 0.19, w, wallHeight, 0.38, wallMat);
    createWall(0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
    createWall(w - 0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
  }

  // Центрируем камеру относительно дома
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