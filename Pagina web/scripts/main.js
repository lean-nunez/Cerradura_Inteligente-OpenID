// =============================
// 🌐 OPEN ID - SMART LOCK SITE
// Animaciones + Fondo tipo "Matrix Azul"
// =============================

// ----- MATRIX BACKGROUND -----
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
document.body.prepend(canvas);

canvas.style.position = "fixed";
canvas.style.top = "0";
canvas.style.left = "0";
canvas.style.zIndex = "-2";
canvas.style.width = "100%";
canvas.style.height = "100%";
canvas.style.backgroundColor = "#010a13";

let width, height, columns, drops;
const fontSize = 16;
const letters = "01#@ΔΞΛΩ≡ΦΨΣ∑αβγδεζηθικλμνξοπρστυφχψω".split("");

function resizeCanvas() {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;
  columns = Math.floor(width / fontSize);
  drops = Array(columns).fill(1);
}
resizeCanvas();

function drawMatrix() {
  ctx.fillStyle = "rgba(0, 10, 26, 0.1)";
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = "#00bfff";
  ctx.font = `${fontSize}px monospace`;

  for (let i = 0; i < drops.length; i++) {
    const text = letters[Math.floor(Math.random() * letters.length)];
    ctx.fillText(text, i * fontSize, drops[i] * fontSize);

    if (drops[i] * fontSize > height && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i]++;
  }
}

setInterval(drawMatrix, 40);
window.addEventListener("resize", resizeCanvas);

// ----- BOTONES ANIMADOS -----
const buttons = document.querySelectorAll(".btn");
buttons.forEach(btn => {
  btn.addEventListener("mouseenter", () => {
    btn.style.transform = "scale(1.15)";
    btn.style.boxShadow = "0 0 30px #00eaff";
  });
  btn.addEventListener("mouseleave", () => {
    btn.style.transform = "scale(1)";
    btn.style.boxShadow = "0 0 10px rgba(0, 191, 255, 0.5)";
  });
});

// ----- EFECTO DE SCROLL SUAVE -----
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function(e) {
    e.preventDefault();
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth"
    });
  });
});

// ----- ANIMACIÓN AL CARGAR -----
window.addEventListener("load", () => {
  const header = document.querySelector("header");
  header.style.opacity = 0;
  header.style.transition = "opacity 2s ease";
  setTimeout(() => (header.style.opacity = 1), 300);

  const sections = document.querySelectorAll("section");
  sections.forEach((section, i) => {
    section.style.opacity = 0;
    section.style.transform = "translateY(20px)";
    section.style.transition = "opacity 0.8s ease, transform 0.8s ease";
    setTimeout(() => {
      section.style.opacity = 1;
      section.style.transform = "translateY(0)";
    }, 500 + i * 200);
  });
});
