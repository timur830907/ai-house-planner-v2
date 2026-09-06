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
  const shape = (layoutData.shape || "rectangle").toLowerCase().strip();

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
    createWall(x1 + rw / 2, wallHeight / 2, y1, rw, wallHeight, 0.15, intWallMat);
    createWall(x1 + rw / 2, wallHeight / 2, y2, rw, wallHeight, 0.15, intWallMat);
    createWall(x1, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);
    createWall(x2, wallHeight / 2, y1 + rl / 2, 0.15, wallHeight, rl, intWallMat);

    // Отрисовка 3D-дверей (полотна + ручка)
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

    // Добавление текстовой таблички с именем и площадью комнаты над полом
    createRoomLabel(rName, area, x1 + rw / 2, y1 + rl / 2);
  });

  // 2. Внешняя геометрия (поддержка Г-образной, Т-образной, Круглой, Эллиптической и Прямоугольной форм)
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
    // Отрисовка Г-образного контура стен с вырезом
    const cutW = w * 0.4;
    const cutL = l * 0.4;

    // 6 внешних стен Г-образного периметра
    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);                                // Север
    createWall(0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);                                // Запад
    createWall((w - cutW) / 2, wallHeight / 2, l - 0.19, w - cutW, wallHeight, 0.38, wallMat);            // Юг (короткий)
    createWall(w - cutW, wallHeight / 2, l - cutL / 2, 0.38, wallHeight, cutL, wallMat);                 // Внутренний угол Y
    createWall(w - cutW / 2, wallHeight / 2, l - cutL, cutW, wallHeight, 0.38, wallMat);                  // Внутренний угол X
    createWall(w - 0.19, wallHeight / 2, (l - cutL) / 2, 0.38, wallHeight, l - cutL, wallMat);            // Восток (короткий)

  } else if (shape === "t_shape" || shape === "т-образный") {
    // Отрисовка Т-образного контура
    const wingW = w * 0.3;
    const wingL = l * 0.4;

    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);                                // Север
    createWall(0.19, wallHeight / 2, wingL / 2, 0.38, wallHeight, wingL, wallMat);                        // Верх Запад
    createWall(w - 0.19, wallHeight / 2, wingL / 2, 0.38, wallHeight, wingL, wallMat);                    // Верх Восток
    createWall(wingW / 2, wallHeight / 2, wingL, wingW, wallHeight, 0.38, wallMat);                      // Выступ Запад
    createWall(w - wingW / 2, wallHeight / 2, wingL, wingW, wallHeight, 0.38, wallMat);                  // Выступ Восток
    createWall(wingW + 0.19, wallHeight / 2, wingL + (l - wingL) / 2, 0.38, wallHeight, l - wingL, wallMat);// Низ Запад
    createWall(w - wingW - 0.19, wallHeight / 2, wingL + (l - wingL) / 2, 0.38, wallHeight, l - wingL, wallMat); // Низ Восток
    createWall(w / 2, wallHeight / 2, l - 0.19, w - wingW * 2, wallHeight, 0.38, wallMat);                // Юг
  } else {
    // Стандартный прямоугольный дом
    createWall(w / 2, wallHeight / 2, 0.19, w, wallHeight, 0.38, wallMat);
    createWall(w / 2, wallHeight / 2, l - 0.19, w, wallHeight, 0.38, wallMat);
    createWall(0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
    createWall(w - 0.19, wallHeight / 2, l / 2, 0.38, wallHeight, l, wallMat);
  }

  // 3. Расстановка мебели и подсоединение DragControls
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