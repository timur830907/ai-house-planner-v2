const API_URL = "https://ai-house-planner-v2.onrender.com";
let currentPlans = [];

async function generatePlans() {
  const areaInput = document.getElementById("areaInput");
  const area = parseFloat(areaInput.value) || 100;
  
  const roomCheckboxes = document.querySelectorAll('input[name="rooms"]:checked');
  let rooms = Array.from(roomCheckboxes).map(cb => cb.value);
  if (rooms.length === 0) rooms = ["Прихожая", "Гостиная", "Кухня", "Ванная", "Спальня 1"];

  const statusElement = document.getElementById("statusMessage");
  if (statusElement) statusElement.innerText = "Генерация 3D модели...";

  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ area, rooms })
    });

    if (!response.ok) throw new Error("Ошибка генерации");

    const data = await response.json();
    currentPlans = data.plans || [];

    if (statusElement) statusElement.innerText = `Успешно! Построено 3D вариантов: ${currentPlans.length}`;

    // Запускаем 3D визуализацию первого варианта
    if (currentPlans.length > 0 && typeof render3DLayout === "function") {
      document.getElementById("viewer3d").style.display = "block";
      render3DLayout(currentPlans[0]);
    }
  } catch (error) {
    console.error(error);
    if (statusElement) statusElement.innerText = "Ошибка генерации.";
  }
}

async function downloadExport(planIndex, format) {
  if (!currentPlans[planIndex]) {
    alert("Сначала сгенерируйте планировку!");
    return;
  }

  const planData = currentPlans[planIndex];
  const endpoint = format === "pdf" ? "/export/pdf" : "/export/dxf";

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(planData)
    });

    if (!response.ok) throw new Error(`Ошибка экспорта`);

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = `house_plan_${planIndex + 1}.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (error) {
    console.error(error);
    alert(`Не удалось скачать ${format.toUpperCase()}`);
  }
}