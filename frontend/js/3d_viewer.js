function init3DView(containerId, layoutData) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(10, 15, 20);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
  dirLight.position.set(10, 20, 10);
  scene.add(dirLight);

  const layout = layoutData.layout || layoutData;
  const wallHeight = 2.8;
  const wallMaterial = new THREE.MeshLambertMaterial({ color: 0xcccccc });
  const floorMaterial = new THREE.MeshLambertMaterial({ color: 0xdedede });

  Object.keys(layout).forEach((roomName) => {
    const room = layout[roomName];
    const bounds = room.bounds || [0, 0, 4, 4];
    const x1 = bounds[0], y1 = bounds[1], x2 = bounds[2], y2 = bounds[3];
    const width = x2 - x1;
    const depth = y2 - y1;

    // Пол
    const floorGeo = new THREE.PlaneGeometry(width, depth);
    const floorMesh = new THREE.Mesh(floorGeo, floorMaterial);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.position.set(x1 + width / 2, 0, y1 + depth / 2);
    scene.add(floorMesh);

    // Стены (Box)
    const wallGeo = new THREE.BoxGeometry(width, wallHeight, depth);
    const wallMesh = new THREE.Mesh(wallGeo, wallMaterial);
    wallMesh.position.set(x1 + width / 2, wallHeight / 2, y1 + depth / 2);
    scene.add(wallMesh);
  });

  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  animate();
}