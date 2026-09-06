// -------------------------------------------------------------
// Основная генерация 3D сцены
// -------------------------------------------------------------

function update3DLayout(layoutData) {
  if (!layoutGroup) return;

  // Очистка старых DragControls и объектов мебели
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
  
  // Исправлено: безопасное приведение формы к нижнему регистру и удаление пробелов через .trim()
  const rawShape = layoutData.shape || "rectangle";
  const shape = String(rawShape).toLowerCase().trim();

  const wallMat = new THREE.MeshStandardMaterial({ color: 0xbdc3c7, roughness: 0.6 });
  const intWallMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.6 });
  const wallHeight = dim.height || 2.8;

  // 1. Полы, перегородки, двери и 3D-надписи
  Object.keys(rooms).forEach((rName) => {
    const room = rooms[rName];
    if (!room.bounds) return;
    const [x1, y1, x2, y2] = room.bounds;
    const rw = x2 - x1;
    const rl = y2 - y1;
    const area = rw * rl;

    // Отрисовка пола
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

    // Внутренние стены комнат
    if (typeof createWall === "function") {
      createWall(x1 + rw / 2, wallHeight / 2, y1, rw, wallHeight, 0.15, intWallMat);
      createWall(x1 + rw / 2, wallHeight / 2, y2, rw, wallHeight, 0.15, intWallMat);
      createWall(x1, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
      createWall(x2, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
    }

    // Отрисовка 3D-дверей (полотна + ручка)
    if (room.doors && Array.isArray(room.doors) && typeof createDoor === "function") {
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

    // Добавление текстовой таблички с именем и площадью комнаты над полом
    if (typeof createRoomLabel === "function") {
      createRoomLabel(rName, area, x1 + rw / 2, y1 + rl / 2);
    }
  });

  // 2. Внешняя геометрия (поддержка Г-образной, Т-образной, Круглой, Эллиптической и Прямоугольной форм)
  const w = dim.width;
  const l = dim.length;

  if (typeof createWall === "function") {
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
      createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);
      createWall(w / 2, wallHeight / 2, l - 0.19, w, wallHeight, 0.38, wallMat);
      createWall(0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
      createWall(w - 0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
    }
  }

  // 3. Расстановка мебели и подсоединение DragControls
  furniture.forEach((item) => {
    if (!item.pos || !item.size) return;
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