let scene, camera, renderer, controls;
let layoutGroup;

function init3DViewer(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // 1. Создание сцены
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a1a);

  // 2. Камера
  camera = new THREE.PerspectiveCamera(
    45, 
    container.clientWidth / container.clientHeight, 
    0.1, 
    1000
  );
  camera.position.set(15, 20, 25);

  // 3. Рендерер
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  // 4. Управление камерой (OrbitControls)
  if (typeof THREE.OrbitControls !== 'undefined') {
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
  }

  // 5. Освещение
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(20, 40, 20);
  dirLight.castShadow = true;
  scene.add(dirLight);

  // Сетевая сетка (Grid)
  const gridHelper = new THREE.GridHelper(30, 30, 0x444444, 0x222222);
  scene.add(gridHelper);

  // Группа для элементов дома
  layoutGroup = new THREE.Group();
  scene.add(layoutGroup);

  // Анимация / Рендеринг
  function animate() {
    requestAnimationFrame(animate);
    if (controls) controls.update();
    renderer.render(scene, camera);
  }
  animate();

  // Ресайз при изменении окна
  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });
}

function update3DLayout(layoutData) {
  if (!layoutGroup) return;

  // Очистка предыдущей модели
  while (layoutGroup.children.length > 0) {
    const obj = layoutGroup.children[0];
    layoutGroup.remove(obj);
  }

  const wallHeight = 2.8;
  const wallThickness = 0.2;
  const wallMaterial = new THREE.MeshLambertMaterial({ color: 0xbdc3c7 });
  const floorMaterial = new THREE.MeshLambertMaterial({ color: 0xecf0f1 });

  // Цвета для разных типов комнат
  const roomColors = [0x3498db, 0xe74c3c, 0x2ecc71, 0xf1c40f, 0x9b59b6];
  let colorIdx = 0;

  const rooms = layoutData.rooms || layoutData;

  Object.keys(rooms).forEach((roomName) => {
    const room = rooms[roomName];
    const bounds = room.bounds || [0, 0, 4, 4];
    const [x1, y1, x2, y2] = bounds;

    const width = x2 - x1;
    const depth = y2 - y1;
    const color = roomColors[colorIdx % roomColors.length];
    colorIdx++;

    // Создание пола комнаты
    const floorGeo = new THREE.PlaneGeometry(width, depth);
    const customFloorMat = new THREE.MeshLambertMaterial({ color: color, side: THREE.DoubleSide });
    const floorMesh = new THREE.Mesh(floorGeo, customFloorMat);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.position.set(x1 + width / 2, 0.01, y1 + depth / 2);
    layoutGroup.add(floorMesh);

    // Внешние стены по периметру прямоугольника комнаты
    const wallBoxGeo = new THREE.BoxGeometry(width, wallHeight, wallThickness);
    
    // Южная стена
    const wallS = new THREE.Mesh(wallBoxGeo, wallMaterial);
    wallS.position.set(x1 + width / 2, wallHeight / 2, y1);
    layoutGroup.add(wallS);

    // Северная стена
    const wallN = new THREE.Mesh(wallBoxGeo, wallMaterial);
    wallN.position.set(x1 + width / 2, wallHeight / 2, y2);
    layoutGroup.add(wallN);

    // Западная стена
    const wallWestGeo = new THREE.BoxGeometry(wallThickness, wallHeight, depth);
    const wallW = new THREE.Mesh(wallWestGeo, wallMaterial);
    wallW.position.set(x1, wallHeight / 2, y1 + depth / 2);
    layoutGroup.add(wallW);

    // Восточная стена
    const wallE = new THREE.Mesh(wallWestGeo, wallMaterial);
    wallE.position.set(x2, wallHeight / 2, y1 + depth / 2);
    layoutGroup.add(wallE);
  });
}