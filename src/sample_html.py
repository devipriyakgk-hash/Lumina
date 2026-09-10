"""A small restaurant page planted with every issue Lumina checks."""

BROKEN_HTML = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body { margin: 0; font-family: Georgia, serif; background: #f3eee6; color: #5c5348; }
      .top { display: flex; justify-content: space-between; padding: 18px 40px; background: #ebe4d8; }
      .logo { letter-spacing: 0.28em; text-transform: uppercase; font-size: 13px; }
      nav a { margin-left: 22px; color: #8a7f70; text-decoration: none; }
      .hero { padding: 64px 40px 40px; background: #e7dfd2; }
      .hero h2 { font-weight: 400; font-size: 42px; margin: 0 0 12px; max-width: 14ch; }
      .cta { margin-top: 16px; padding: 12px 22px; background: #ddd4c6; border: 0; color: #6a5f52; }
      .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; padding: 28px 40px; }
      figure { margin: 0; background: #e8e0d4; }
      figcaption { padding: 10px 12px; font-size: 13px; }
      form { padding: 8px 40px 48px; }
      input { display: block; width: 280px; margin: 8px 0 14px; padding: 10px; }
    </style>
  </head>
  <body>
    <div class="top">
      <div class="logo">Summit Atelier</div>
      <nav>
        <a href="/menu">Menu</a>
        <a href="/book">Reservations</a>
        <a href="/more"></a>
      </nav>
    </div>
    <div class="hero">
      <h2>A quieter table, season by season.</h2>
      <p>Private dining in the old mill. Low light, linen, and a kitchen that changes with the valley.</p>
      <button class="cta"></button>
    </div>
    <div class="grid">
      <figure>
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect fill='%23c9b496' width='640' height='360'/%3E%3Ctext x='50%25' y='54%25' fill='%238c7358' font-size='28' text-anchor='middle' font-family='Georgia'%3EOrchard%3C/text%3E%3C/svg%3E" width="640" height="360" />
        <figcaption>Late orchard fruit</figcaption>
      </figure>
      <figure>
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect fill='%23b7c3b0' width='640' height='360'/%3E%3Ctext x='50%25' y='54%25' fill='%23788870' font-size='28' text-anchor='middle' font-family='Georgia'%3EHerb%3C/text%3E%3C/svg%3E" width="640" height="360" />
        <figcaption>Herb oil</figcaption>
      </figure>
      <figure>
        <img alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect fill='%23c1a090' width='640' height='360'/%3E%3Ctext x='50%25' y='54%25' fill='%23886658' font-size='28' text-anchor='middle' font-family='Georgia'%3EFire%3C/text%3E%3C/svg%3E" width="640" height="360" />
        <figcaption>Open fire</figcaption>
      </figure>
    </div>
    <form>
      <h4>Join the list</h4>
      <input type="text" placeholder="Name" />
      <input id="mail" type="email" placeholder="Email" />
      <input id="mail" type="text" placeholder="Party size" />
      <button type="button" class="cta">Submit</button>
    </form>
  </body>
</html>
"""
