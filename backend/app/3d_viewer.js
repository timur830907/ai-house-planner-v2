function render3DLayout(planData) {
  const container = document.getElementById('viewer3d');
  if (!container) return;
  
  container.innerHTML = ''; // Очищаем предыдущую сцену

  // 1. Создаем сцену и камеру
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a1a);

  const camera = new THREE.PerspectiveCamera(
    45, 
    container.clientWidth / container.clientHeight, 
    0.1, 
    1000
  );
  camera.position.set(15, 20, 25);
  camera.lookAt(5, 0, 5);

  // 2. Инициализируем рендерер
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  // 3. Добавляем освещение
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
  dirLight.position.set(10, 20, 10);
  scene.add(dirLight);

  // 4. Сетка пола
  const gridHelper = new THREE.GridHelper(30, 30, 0x444444, 0x222222);
  scene.add(gridHelper);

  // 5. Построение 3D стен и полов комнат
  const layout = planData.layout || {};
  Object.keys(layout).forEach((roomName) => {
    const room = layout[roomName];
    const bounds = room.bounds || [0, 0, 5, 5];
    
    const width = bounds[2] || room.width || 4;
    const height = bounds[3] || room.height || 4;
    const x = bounds[0] || 0;
    const z = bounds[1] || 0;

    // Пол комнаты
    const floorGeo = new THREE.PlaneGeometry(width, height);
    const floorMat = new THREE.MeshLambertMaterial({ 
      color: 0x2b5c8f, 
      side: THREE.DoubleSide 
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = Math.PI / 2;
    floor.position.set(x + width / 2, 0.01, z + height / 2);
    scene.add(floor);

    // Каркас стен
    const wallGeo = new THREE.BoxGeometry(width, 2.5, height);
    const wallMat = new THREE.MeshLambertMaterial({ 
      color: 0x00ffcc, 
      wireframe: true 
    });
    const wall = new THREE.Mesh(wallGeo, wallMat);
    wall.position.set(x + width / 2, 1.25, z + height / 2);
    scene.add(wall);
  });

  // 6. Цикл анимации (рендеринг)
  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  animate();
}