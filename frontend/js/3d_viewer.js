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

function update3DLayout(layoutData) {
  if (!layoutGroup) return;

  // Очистка старой сцены и отключение старых контроллеров
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

  // 1. Полы и перегородки
  Object.keys(rooms).forEach((rName) => {
    const room = rooms[rName];
    const [x1, y1, x2, y2] = room.bounds;
    const rw = x2 - x1;
    const rl = y2 - y1;

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

    createWall(x1 + rw / 2, wallHeight / 2, y1, rw, wallHeight, 0.15, intWallMat);
    createWall(x1 + rw / 2, wallHeight / 2, y2, rw, wallHeight, 0.15, intWallMat);
    createWall(x1, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
    createWall(x2, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
  });

  // 2. Внешняя геометрия
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

  // 3. Мебель + сохранение для перетаскивания
  furniture.forEach((item) => {
    const [cx, cy] = item.pos;
    const [fw, fl, fh] = item.size;

    const fGeo = new THREE.BoxGeometry(fw, fh, fl);
    const fMat = new THREE.MeshStandardMaterial({ color: item.color || 0x34495e });
    const fMesh = new THREE.Mesh(fGeo, fMat);
    fMesh.position.set(cx, fh / 2 + 0.02, cy);
    fMesh.castShadow = true;
    fMesh.userData = { defaultY: fh / 2 + 0.02 }; // Фиксируем высоту над полом

    layoutGroup.add(fMesh);
    furnitureObjects.push(fMesh); // Добавляем в массив мебели
  });

  // Инициализация DragControls для мебели
  if (furnitureObjects.length > 0 && typeof THREE.DragControls !== 'undefined') {
    dragControls = new THREE.DragControls(furnitureObjects, activeCamera, renderer.domElement);

    dragControls.addEventListener('dragstart', (event) => {
      if (controls) controls.enabled = false; // Блокируем вращение камеры
    });

    dragControls.addEventListener('drag', (event) => {
      // Сохраняем объект строго на уровне пола при перемещении
      if (event.object.userData.defaultY) {
        event.object.position.y = event.object.userData.defaultY;
      }
    });

    dragControls.addEventListener('dragend', (event) => {
      if (controls && !is2DMode) controls.enabled = true; // Возвращаем управление камерой
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