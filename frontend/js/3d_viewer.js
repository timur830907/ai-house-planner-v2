let scene, cameraPersp, cameraOrtho, activeCamera, renderer, controls;
let layoutGroup;
let is2DMode = false;

function init3DViewer(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf4f6f7);

  const aspect = container.clientWidth / container.clientHeight;
  
  // 3D Перспективная камера
  cameraPersp = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
  cameraPersp.position.set(18, 22, 26);

  // 2D Ортографическая камера
  const d = 15;
  cameraOrtho = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 0.1, 1000);
  cameraOrtho.position.set(0, 50, 0);
  cameraOrtho.lookAt(0, 0, 0);

  activeCamera = cameraPersp;

  // Рендерер с PBR и мягкими тенями
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding;

  container.appendChild(renderer.domElement);

  if (typeof THREE.OrbitControls !== 'undefined') {
    controls = new THREE.OrbitControls(cameraPersp, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.05; // Не уходить под пол
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

  window.addEventListener('resize', () => {
    const w = container.clientWidth;
    const h = container.clientHeight;
    const asp = w / h;

    cameraPersp.aspect = asp;
    cameraPersp.updateProjectionMatrix();

    cameraOrtho.left = -d * asp;
    cameraOrtho.right = d * asp;
    cameraOrtho.top = d;
    cameraOrtho.bottom = -d;
    cameraOrtho.updateProjectionMatrix();

    renderer.setSize(w, h);
  });
}

function setupLighting() {
  const ambient = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambient);

  const sun = new THREE.DirectionalLight(0xfff5e6, 1.2);
  sun.position.set(20, 35, 15);
  sun.castShadow = true;
  sun.shadow.mapSize.width = 2048;
  sun.shadow.mapSize.height = 2048;
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 100;
  
  const shadowCamSize = 25;
  sun.shadow.camera.left = -shadowCamSize;
  sun.shadow.camera.right = shadowCamSize;
  sun.shadow.camera.top = shadowCamSize;
  sun.shadow.camera.bottom = -shadowCamSize;
  sun.shadow.bias = -0.0005;

  scene.add(sun);
}

function toggleViewMode(mode2D) {
  is2DMode = mode2D;
  if (is2DMode) {
    activeCamera = cameraOrtho;
    if (controls) controls.enabled = false;
  } else {
    activeCamera = cameraPersp;
    if (controls) controls.enabled = true;
  }
}

function update3DLayout(layoutData) {
  if (!layoutGroup) return;

  while (layoutGroup.children.length > 0) {
    layoutGroup.remove(layoutGroup.children[0]);
  }

  const dim = layoutData.dimensions || { width: 10, length: 12, height: 2.8 };
  const rooms = layoutData.rooms || {};
  const furniture = layoutData.furniture || [];

  // 1. Покрытие пола (PBR)
  Object.keys(rooms).forEach((rName) => {
    const room = rooms[rName];
    const [x1, y1, x2, y2] = room.bounds;
    const rw = x2 - x1;
    const rl = y2 - y1;

    const floorGeo = new THREE.PlaneGeometry(rw, rl);
    const isTile = room.floor_type === "tile";
    
    const floorMat = new THREE.MeshStandardMaterial({
      color: isTile ? 0xdcdde1 : 0xd2b48c,
      roughness: isTile ? 0.2 : 0.6,
      metalness: 0.05
    });

    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.position.set(x1 + rw / 2, 0.01, y1 + rl / 2);
    floorMesh.receiveShadow = true;
    layoutGroup.add(floorMesh);
  });

  // 2. Внешний периметр и перегородки
  const wallMat = new THREE.MeshStandardMaterial({
    color: 0xecf0f1,
    roughness: 0.8,
    metalness: 0.1
  });

  const wallHeight = dim.height || 2.8;

  // Отрисовка внешней рамки
  const extThick = layoutData.wall_thickness?.external || 0.38;
  createWall(dim.width / 2, wallHeight / 2, extThick / 2, dim.width, wallHeight, extThick, wallMat);
  createWall(dim.width / 2, wallHeight / 2, dim.length - extThick / 2, dim.width, wallHeight, extThick, wallMat);
  createWall(extThick / 2, wallHeight / 2, dim.length / 2, extThick, wallHeight, dim.length, wallMat);
  createWall(dim.width - extThick / 2, wallHeight / 2, dim.length / 2, extThick, wallHeight, dim.length, wallMat);

  // 3. Мебель с реалистичной фаской
  furniture.forEach((item) => {
    const [cx, cy] = item.pos;
    const [fw, fl, fh] = item.size;

    const fGeo = new THREE.BoxGeometry(fw, fh, fl);
    const fMat = new THREE.MeshStandardMaterial({
      color: item.color || 0x34495e,
      roughness: 0.5,
      metalness: 0.1
    });

    const fMesh = new THREE.Mesh(fGeo, fMat);
    fMesh.position.set(cx, fh / 2 + 0.02, cy);
    fMesh.castShadow = true;
    fMesh.receiveShadow = true;
    layoutGroup.add(fMesh);
  });
}

function createWall(x, y, z, w, h, d, mat) {
  const geo = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  layoutGroup.add(mesh);
}