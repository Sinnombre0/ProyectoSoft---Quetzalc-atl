/**
 * fireflies.js
 * Canvas 2D que anima luciérnagas flotantes.
 * Equivalente al componente FireflyBackground.tsx de Lovable.
 */

(function () {
  const canvas = document.getElementById("firefly-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const COUNT = 35; // número de luciérnagas
  let flies = [];
  let W, H;

  /* ── Resize ── */
  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  window.addEventListener("resize", resize);
  resize();

  /* ── Crear luciérnaga ── */
  function createFly() {
    return {
      x:    Math.random() * W,
      y:    Math.random() * H,
      r:    Math.random() * 2.5 + 1,       // radio del punto
      glow: Math.random() * 18 + 8,        // radio del halo
      vx:   (Math.random() - 0.5) * 0.55,  // velocidad x
      vy:   (Math.random() - 0.5) * 0.55,  // velocidad y
      alpha:    Math.random(),
      alphaDir: Math.random() > 0.5 ? 1 : -1,
      alphaSpd: Math.random() * 0.008 + 0.003,
      phase:    Math.random() * Math.PI * 2,  // para movimiento sinusoidal
    };
  }

  flies = Array.from({ length: COUNT }, createFly);

  /* ── Dibujar una luciérnaga ── */
  function drawFly(f, t) {
    // Movimiento ondulante
    const ox = Math.sin(t * 0.0004 + f.phase) * 40;
    const oy = Math.cos(t * 0.0005 + f.phase * 1.3) * 30;
    const px = f.x + ox;
    const py = f.y + oy;

    // Parpadeo de alpha
    f.alpha += f.alphaSpd * f.alphaDir;
    if (f.alpha >= 1) { f.alpha = 1; f.alphaDir = -1; }
    if (f.alpha <= 0.1) { f.alpha = 0.1; f.alphaDir = 1; }

    // Halo exterior
    const grad = ctx.createRadialGradient(px, py, 0, px, py, f.glow);
    grad.addColorStop(0,   `oklch(0.93 0.18 100 / ${(f.alpha * 0.9).toFixed(2)})`);
    grad.addColorStop(0.4, `oklch(0.9 0.2 105 / ${(f.alpha * 0.4).toFixed(2)})`);
    grad.addColorStop(1,   `transparent`);
    ctx.beginPath();
    ctx.arc(px, py, f.glow, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();

    // Punto central
    ctx.beginPath();
    ctx.arc(px, py, f.r, 0, Math.PI * 2);
    ctx.fillStyle = `oklch(0.97 0.08 100 / ${f.alpha.toFixed(2)})`;
    ctx.fill();

    // Movimiento de posición base lento
    f.x += f.vx;
    f.y += f.vy;

    // Rebote en bordes
    if (f.x < -50)  f.x = W + 50;
    if (f.x > W + 50) f.x = -50;
    if (f.y < -50)  f.y = H + 50;
    if (f.y > H + 50) f.y = -50;
  }

  /* ── Loop ── */
  function loop(t) {
    // Modificacion al color del fondo por un azul de medianoche
    ctx.fillStyle = `oklch(0.22 0.12 250)`; 
    ctx.fillRect(0, 0, W, H);
    flies.forEach(f => drawFly(f, t));
    requestAnimationFrame(loop);
  }

  requestAnimationFrame(loop);
})();
