import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';

export function init3DView(containerId, layoutData) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(10, 15, 20);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    
    // Свет
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
    dirLight.position.set(10, 20, 10);
    scene.add(dirLight);

    // Построение 3D стен по геометрии из JSON
    const wallHeight = 2.8;
    const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xcccccc });
    const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xdedede });

    for (const [name, room] of Object.entries(layoutData)) {
        const [x1, y1, x2, y2] = room.bounds;
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
        
        // Визуализация проволочной рамки для разделения комнат
        const wireframe = new THREE.WireframeGeometry(wallGeo);
        const line = new THREE.LineSegments(wireframe, new THREE.LineBasicMaterial({ color: 0x000000 }));
        wallMesh.add(line);

        scene.add(wallMesh);
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}