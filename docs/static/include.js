async function includeHTMLSimple(selector, file) {
  const element = document.querySelector(selector);
  if (!element) return;

  try {
    const response = await fetch(file);
    if (!response.ok) throw new Error(`No se pudo cargar ${file}`);
    const html = await response.text();
    element.innerHTML = html;
  } catch (error) {
    console.error(error);
  }
}

async function includeHTML(selector, file) {
  const element = document.querySelector(selector);
  if (!element) return;

  const cached = sessionStorage.getItem(file);
  if (cached) {
    element.innerHTML = cached;
    return;
  }

  const response = await fetch(file);
  const html = await response.text();
  element.innerHTML = html;
  sessionStorage.setItem(file, html);
}


// cuando el DOM está listo
document.addEventListener("DOMContentLoaded", () => {
  includeHTML("nav", "partials/navbar.html");
  //includeHTML("footer", "partials/footer.html");
});