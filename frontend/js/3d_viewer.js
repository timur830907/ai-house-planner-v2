let scene, camera, renderer, controls;
let layoutGroup;

function init3DViewer(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a1a);

  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(20, 25, 30);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  if (typeof THREE.OrbitControls !== 'undefined') {
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
  }

  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(20, 40, 20);
  scene.add(dirLight);

  scene.add(new THREE.GridHelper(40, 40, 0x555555, 0x222222));

  layoutGroup = new THREE.Group();
  scene.add(layoutGroup);

  function animate() {
    requestAnimationFrame(animate);
    if (controls) controls.update();
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });
}

function update3DLayout(layoutData) {
  if (!layoutGroup) return;

  while (layoutGroup.children.length > 0) {
    layoutGroup.remove(layoutGroup.children[0]);
  }

  const wallHeight = 2.8;
  const wallThickness = 0.15;
  const wallMat = new THREE.MeshLambertMaterial({ color: 0xbdc3c7 });

  const roomColors = [0x3498db, 0xe74c3c, 0x2ecc71, 0xf1c40f, 0x9b59b6];
  let colorIdx = 0;

  const rooms = layoutData.rooms || {};

  // Отрисовка комнат и стен
  Object.keys(rooms).forEach((roomName) => {
    const room = rooms[roomName];
    if (room.type === "void") return;

    const bounds = room.bounds || room;
    if (!Array.isArray(bounds) || bounds.length < 4) return;

    const [x1, y1, x2, y2] = bounds;
    const width = x2 - x1;
    const depth = y2 - y1;

    // Пол
    const floorGeo = new THREE.PlaneGeometry(width, depth);
    const floorMat = new THREE.MeshLambertMaterial({ 
      color: roomColors[colorIdx % roomColors.length], 
      side: THREE.DoubleSide 
    });
    colorIdx++;

    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.position.set(x1 + width / 2, 0.02, y1 + depth / 2);
    layoutGroup.add(floorMesh);

    // Стены
    const wBox = new THREE.BoxGeometry(width, wallHeight, wallThickness);
    const dBox = new THREE.BoxGeometry(wallThickness, wallHeight, depth);

    const wallS = new THREE.Mesh(wBox, wallMat);
    wallS.position.set(x1 + width / 2, wallHeight / 2, y1);
    layoutGroup.add(wallS);

    const wallN = new THREE.Mesh(wBox, wallMat);
    wallN.position.set(x1 + width / 2, wallHeight / 2, y2);
    layoutGroup.add(wallN);

    const wallW = new THREE.Mesh(dBox, wallMat);
    wallW.position.set(x1, wallHeight / 2, y1 + depth / 2);
    layoutGroup.add(wallW);

    const wallE = new THREE.Mesh(dBox, wallMat);
    wallE.position.set(x2, wallHeight / 2, y1 + depth / 2);
    layoutGroup.add(wallE);
  });

  // Отрисовка мебели
  const furniture = layoutData.furniture || [];
  furniture.forEach((item) => {
    const [cx, cy] = item.pos;
    const [fw, fl] = item.size;
    const fh = 0.6; // Высота предметов мебели

    const fGeo = new THREE.BoxGeometry(fw, fh, fl);
    const fMat = new THREE.MeshLambertMaterial({ color: item.color || 0x333333 });
    const fMesh = new THREE.Mesh(fGeo, fMat);
    fMesh.position.set(cx, fh / 2, cy);
    layoutGroup.add(fMesh);
  });
}