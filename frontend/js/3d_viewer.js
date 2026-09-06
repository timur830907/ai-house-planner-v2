let scene, cameraPersp, cameraOrtho, activeCamera, renderer, controls;
let layoutGroup;
let is2DMode = false;

// Переменные для интерактивного перетаскивания мебели
let furnitureObjects = [];
let dragControls = null;

function init3DViewer(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f2f5);

  const aspect = container.clientWidth / container.clientHeight;

  cameraPersp = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
  cameraPersp.position.set(18, 22, 26);

  const d = 15;
  cameraOrtho = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 0.1, 1000);
  cameraOrtho.position.set(0, 50, 0);
  cameraOrtho.lookAt(0, 0, 0);

  activeCamera = cameraPersp;

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  container.appendChild(renderer.domElement);

  if (typeof THREE.OrbitControls !== 'undefined') {
    controls = new THREE.OrbitControls(cameraPersp, renderer.domElement);
    controls.enableDamping = true;
  }

  setupLighting();

  layoutGroup = new THREE.Group();
  scene.add(layoutGroup);

  function animate() {
    requestAnimationFrame(animate);
    if (controls && !is2DMode) controls.update();
    renderer.render(scene, activeCamera);
  }
  animate();
}

function setupLighting() {
  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const sun = new THREE.DirectionalLight(0xffffff, 0.8);
  sun.position.set(20, 35, 15);
  sun.castShadow = true;
  scene.add(sun);
}

function toggleViewMode(mode2D) {
  is2DMode = mode2D;
  activeCamera = is2DMode ? cameraOrtho : cameraPersp;
  if (controls) controls.enabled = !is2DMode;
}

// -------------------------------------------------------------
// Вспомогательные функции: Названия комнат и Двери
// -------------------------------------------------------------

// Создание спрайта с текстом наименования и площади комнаты
function createRoomLabel(name, area, x, z) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = 256;
  canvas.height = 128;

  ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "#2c3e50";
  ctx.lineWidth = 6;
  ctx.strokeRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#1e272e";
  ctx.font = "Bold 24px Arial";
  ctx.textAlign = "center";
  ctx.fillText(name, 128, 50);

  ctx.fillStyle = "#7f8c8d";
  ctx.font = "20px Arial";
  ctx.fillText(area.toFixed(1) + " м²", 128, 85);

  const texture = new THREE.CanvasTexture(canvas);
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(spriteMaterial);

  sprite.position.set(x, 2.2, z);
  sprite.scale.set(3, 1.5, 1);
  layoutGroup.add(sprite);
}

// Создание 3D-двери с полотном и дверной ручкой
function createDoor(x, y, z, width, height, rotationY) {
  const doorGroup = new THREE.Group();

  // Полотно двери
  const doorGeo = new THREE.BoxGeometry(width, height, 0.08);
  const doorMat = new THREE.MeshStandardMaterial({ color: 0x8e5a2b, roughness: 0.4 });
  const doorMesh = new THREE.Mesh(doorGeo, doorMat);
  doorMesh.position.set(0, height / 2, 0);

  // Дверная ручка
  const handleGeo = new THREE.SphereGeometry(0.05, 8, 8);
  const handleMat = new THREE.MeshStandardMaterial({ color: 0xdcdde1, metalness: 0.8 });
  const handleMesh = new THREE.Mesh(handleGeo, handleMat);
  handleMesh.position.set(width * 0.35, height / 2, 0.06);

  doorGroup.add(doorMesh);
  doorGroup.add(handleMesh);

  doorGroup.position.set(x, y, z);
  doorGroup.rotation.y = rotationY;

  layoutGroup.add(doorGroup);
}

// -------------------------------------------------------------
// Основная генерация сцены
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

  const dim = layoutData.dimensions || { width: 12, length: 14, height: 2.8 };
  const rooms = layoutData.rooms || {};
  const furniture = layoutData.furniture || [];
  const shape = layoutData.shape || "rectangle";

  const wallMat = new THREE.MeshStandardMaterial({ color: 0xbdc3c7, roughness: 0.6 });
  const intWallMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.6 });
  const wallHeight = dim.height || 2.8;

  // 1. Полы, перегородки, двери и 3D-надписи
  Object.keys(rooms).forEach((rName) => {
    const room = rooms[rName];
    const [x1, y1, x2, y2] = room.bounds;
    const rw = x2 - x1;
    const rl = y2 - y1;
    const area = rw * rl;

    // Пол
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

    // Внутренние стены
    createWall(x1 + rw / 2, wallHeight / 2, y1, rw, wallHeight, 0.15, intWallMat);
    createWall(x1 + rw / 2, wallHeight / 2, y2, rw, wallHeight, 0.15, intWallMat);
    createWall(x1, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
    createWall(x2, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);

    // Отрисовка дверей для комнаты
    if (room.doors && Array.isArray(room.doors)) {
      room.doors.forEach((door) => {
        const dWidth = door.width || 0.8;
        if (door.wall === "north") {
          createDoor(x1 + rw * door.pos, 0, y1, dWidth, 2.1, 0);
        } else if (door.wall === "south") {
          createDoor(x1 + rw * door.pos, 0, y2, dWidth, 2.1, 0);
        } else if (door.wall === "west") {
          createDoor(x1, 0, y1 + rl * door.pos, dWidth, 2.1, Math.PI / 2);
        } else if (door.wall === "east") {
          createDoor(x2, 0, y1 + rl * door.pos, dWidth, 2.1, Math.PI / 2);
        }
      });
    }

    // Добавление текстовой надписи в центр комнаты
    createRoomLabel(rName, area, x1 + rw / 2, y1 + rl / 2);
  });

  // 2. Внешние стены
  const w = dim.width;
  const l = dim.length;

  if (shape === "circle" || shape === "ellipse") {
    const rx = w / 2;
    const ry = l / 2;
    const cylGeo = new THREE.CylinderGeometry(rx, rx, wallHeight, 32, 1, true);
    const cylMesh = new THREE.Mesh(cylGeo, wallMat);
    cylMesh.position.set(rx, wallHeight / 2, ry);
    if (shape === "ellipse") cylMesh.scale.set(1, 1, ry / rx);
    layoutGroup.add(cylMesh);
  } else if (shape === "triangle") {
    createWall(w / 2, wallHeight / 2, 0, w, wallHeight, 0.38, wallMat);
    createWall(w / 4, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
    createWall(3 * w / 4, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
  } else {
    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);
    createWall(w / 2, wallHeight / 2, l - 0.19, w, wallHeight, 0.38, wallMat);
    createWall(0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
    createWall(w - 0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
  }

  // 3. Расстановка мебели и привязка DragControls
  furniture.forEach((item) => {
    const [cx, cy] = item.pos;
    const [fw, fl, fh] = item.size;

    const fGeo = new THREE.BoxGeometry(fw, fh, fl);
    const fMat = new THREE.MeshStandardMaterial({ color: item.color || 0x34495e });
    const fMesh = new THREE.Mesh(fGeo, fMat);
    fMesh.position.set(cx, fh / 2 + 0.02, cy);
    fMesh.castShadow = true;
    fMesh.userData = { defaultY: fh / 2 + 0.02 };

    layoutGroup.add(fMesh);
    furnitureObjects.push(fMesh);
  });

  if (furnitureObjects.length > 0 && typeof THREE.DragControls !== 'undefined') {
    dragControls = new THREE.DragControls(furnitureObjects, activeCamera, renderer.domElement);

    dragControls.addEventListener('dragstart', () => {
      if (controls) controls.enabled = false;
    });

    dragControls.addEventListener('drag', (event) => {
      if (event.object.userData.defaultY) {
        event.object.position.y = event.object.userData.defaultY;
      }
    });

    dragControls.addEventListener('dragend', () => {
      if (controls && !is2DMode) controls.enabled = true;
    });
  }
}

function createWall(x, y, z, w, h, d, mat) {
  const geo = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  layoutGroup.add(mesh);
}