/* @site reel : le salon/aménagement sur le vrai site/, construit par python3 site.py (tests/navigateur/lancer.sh).
   - Vues : chaque vue et chaque repère à 1440, 1100 et 390 px : sans erreur de console ni réponse en erreur, images
     chargées, rien ne déborde ; « Position » marque l'élément affiché ; Iso : NE et SO grisés ; Caméra grisée.
   - Plan : douze meubles touchables dans l'état d'origine, chacun touché au centre de sa partie visible ouvre sa propre
     fiche ; #plan?k=enfilade l'ouvre ; la fiche de la table suit l'option Table. Pas de « Comparer » (une variante).
   - Personnaliser : Table, Siège, Décoration (plan et coupes), Bois (rendus iso : une image par valeur) ; chaque
     valeur change ce que montre le dessin, « Valeurs d'origine » revient, le choix tient au rechargement ; sans
     localStorage, les défauts.
   - Dessins : aucun aplat noir, aucun texte hors du viewBox, dans chaque état des options.
   - Explication : 17 cartes « Principe », « Montrer sur le plan », liens vers les deux meubles.
   - Anciennes adresses (salon-v4.html et ses ancres), historique (28 changements, V4.26 en tête, trois versions
     figées) et la page sans JavaScript. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/salon/amenagement/`;
  const VUES = ["plan", "coupes", "iso", "camera", "explication"];
  const LARGEURS = [[1440, 900], [1100, 800], [390, 844]];
  const REPERES = {plan: [""], coupes: ["A", "B", "C", "D"], iso: ["no", "se"], camera: [], explication: [""]};
  const ZONES = ["enfilade", "etageres", "canape", "desserte", "chaises", "table", "table-basse", "siege", "meuble-bas",
                 "ecran", "projecteur", "clim"];
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };
  const egal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  const preparer = async p => {
    p.on("console", m => { if (m.type() === "error") erreurs.push(`console : ${m.text()}`); });
    p.on("pageerror", e => erreurs.push(`page : ${e.message}`));
    p.on("response", r => { if (r.status() >= 400) erreurs.push(`${r.status()} : ${r.url()}`); });
    p.on("requestfailed", r => {
      const raison = (r.failure() || {}).errorText || "";
      if (!raison.includes("ERR_ABORTED")) erreurs.push(`échec : ${r.url()} (${raison})`);
    });
    p.setDefaultTimeout(3000);
    await p.emulateMedia({reducedMotion: "reduce"});
  };
  const sansPolices = ctx => ctx.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                                       r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  const ouvrir = async (p, adresse) => { await p.goto("about:blank"); await p.goto(adresse); };
  const attendre = async (p, condition, arg, message) => {
    try { await p.waitForFunction(condition, arg, {timeout: 3000}); return true; } catch (e) { echecs.push(message); return false; }
  };
  const debordements = p => p.evaluate(() => {
    const l = innerWidth, res = [];
    const vu = e => e && e.checkVisibility({visibilityProperty: true, opacityProperty: true});
    if (document.documentElement.scrollWidth > l) res.push(`page : ${document.documentElement.scrollWidth} px pour ${l}`);
    const section = [...document.querySelectorAll("#contenu > section.vue")].find(s => vu(s));
    const boites = [["barre", document.querySelector("#barre")], ["onglets", document.querySelector("nav.vues")],
                    ["panneau", document.querySelector("#panneau-options")]];
    if (section) for (const sel of [".scene", ".fiche", ".lecture"]) boites.push([sel, section.querySelector(sel)]);
    for (const [nom, e] of boites) {
      if (!vu(e)) continue;
      const r = e.getBoundingClientRect();
      if (r.left < -1 || r.right > l + 1) res.push(`${nom} : de ${Math.round(r.left)} à ${Math.round(r.right)} px pour ${l}`);
      if (nom !== ".scene" && e.scrollWidth > e.clientWidth + 1) res.push(`${nom} : contenu de ${e.scrollWidth} px dans ${e.clientWidth}`);
    }
    return res;
  });
  const imagesChargees = (p, vue) => attendre(p, v => [...document.querySelectorAll(`section[data-vue="${v}"] img`)]
    .filter(i => { for (let x = i; x; x = x.parentElement) if (getComputedStyle(x).display === "none") return false; return true; })
    .every(i => i.complete && i.naturalWidth > 0), vue, `${vue} : image non chargée`);
  const partie = async (nom, f) => {
    try { await f(); } catch (e) { echecs.push(`${nom} : exception : ${e.message.split("\n")[0]}`); }
  };

  await sansPolices(page.context());
  await preparer(page);

  // ------------------------------------------------------------------ toutes les vues, tous les repères
  await partie("vues", async () => {
    for (const [largeur, hauteur] of LARGEURS) {
      await page.setViewportSize({width: largeur, height: hauteur});
      for (const vue of VUES) {
        await ouvrir(page, `${DOC}#${vue}`);
        const ks = await page.evaluate(v => [...document.querySelectorAll(
          `section[data-vue="${v}"] .segments button[data-k]:not(:disabled)`)].map(b => b.dataset.k), vue);
        const attendus = REPERES[vue].filter(k => k !== "");
        verifier(egal(ks, attendus), `${largeur} px, ${vue} : repères ${JSON.stringify(ks)} au lieu de ${JSON.stringify(attendus)}`);
        if (vue === "iso") {
          const gris = await page.evaluate(() => [...document.querySelectorAll(
            'section[data-vue="iso"] .segments button[data-k]:disabled')].map(b => b.dataset.k));
          verifier(egal(gris, ["ne", "so"]), `${largeur} px, iso : grisés ${JSON.stringify(gris)}`);
        }
        if (vue === "camera") {
          const onglet = await page.evaluate(() => {
            const a = document.querySelector('nav.vues a[data-vue="camera"]');
            return a ? a.getAttribute("aria-disabled") : "absent";
          });
          verifier(onglet === "true", `${largeur} px : l'onglet Caméra n'est pas grisé (${onglet})`);
        }
        for (const k of ks.length ? ks : [""]) {
          const t = `${largeur} px, ${vue}${k ? " " + k : ""}`;
          if (k) {
            await page.evaluate(([v, k]) => { location.hash = `#${v}?k=${k}`; }, [vue, k]);
            await attendre(page, ([v, k]) => {
              const e = document.querySelector(`section[data-vue="${v}"] .scene > .element[data-k="${k}"]`);
              return e && e.checkVisibility();
            }, [vue, k], `${t} : l'élément ne s'affiche pas`);
          }
          const e = await page.evaluate(v => ({
            vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
            courant: [...document.querySelectorAll("nav.vues a[aria-current='page']")].map(a => a.dataset.vue),
          }), vue);
          verifier(egal(e.vues, [vue]) && egal(e.courant, [vue]), `${t} : ${JSON.stringify(e)}`);
          if (k && ["coupes", "iso"].includes(vue)) {
            await attendre(page, ([v, k]) => {
              const ici = [...document.querySelectorAll(`section[data-vue="${v}"] .mini [data-k].ici`)].map(x => x.dataset.k);
              return ici.length === 1 && ici[0] === k;
            }, [vue, k], `${t} : « Position » ne marque pas ${k}`);
          }
          await imagesChargees(page, vue);
          const d = await debordements(page);
          verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
        }
      }
    }
  });

  // ------------------------------------------------------------------ plan : les meubles touchables
  const fiche = () => page.evaluate(() => {
    const s = document.querySelector('section[data-vue="plan"]');
    return {hash: location.hash, nom: (s.querySelector(".fiche-nom") || {textContent: ""}).textContent,
            liens: [...s.querySelectorAll(".fiche-meuble a")].map(a => a.textContent),
            corps: s.querySelector(".fiche-meuble").textContent, ici: s.querySelectorAll("rect.zone.ici").length};
  });
  // le point de la zone, non couvert par une zone posée par-dessus, le plus proche du centre de ces points
  const cibles = () => page.evaluate(() => {
    const vu = e => { for (let x = e; x; x = x.parentElement) if (getComputedStyle(x).display === "none") return false; return true; };
    const s = document.querySelector('section[data-vue="plan"]');
    return [...s.querySelectorAll("rect.zone[data-meuble]")].filter(vu).map(z => {
      const b = z.getBoundingClientRect(), pas = Math.max(0.5, Math.min(b.width, b.height) / 16), pts = [];
      for (let x = b.left + pas / 2; x < b.right; x += pas)
        for (let y = b.top + pas / 2; y < b.bottom; y += pas)
          if (document.elementFromPoint(x, y) === z) pts.push([x, y]);
      if (!pts.length) return {id: z.dataset.meuble, n: 0};
      const cx = pts.reduce((a, p) => a + p[0], 0) / pts.length, cy = pts.reduce((a, p) => a + p[1], 0) / pts.length;
      const [x, y] = pts.reduce((m, p) => Math.hypot(p[0] - cx, p[1] - cy) < Math.hypot(m[0] - cx, m[1] - cy) ? p : m);
      return {id: z.dataset.meuble, n: pts.length, x, y};
    });
  });
  const choisir = async (p, o, code) => {
    await p.click("#c-options");
    await attendre(p, () => document.querySelector("#panneau-options").checkVisibility(), null, "le panneau ne s'ouvre pas");
    await p.click(`#panneau-options section[data-o="${o}"] [data-v="${code}"]`);
    await p.keyboard.press("Escape");
  };
  await partie("plan", async () => {
    for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
      const t = `${largeur} px, plan`;
      await page.setViewportSize({width: largeur, height: hauteur});
      await ouvrir(page, DOC + "#plan");
      await page.evaluate(() => localStorage.clear());
      await ouvrir(page, DOC + "#plan");
      let f = await fiche();
      verifier(f.corps.includes("Touchez un meuble pour afficher sa fiche."), `${t} : invite ${JSON.stringify(f)}`);
      const enfilade = 'section[data-vue="plan"] rect.zone[data-meuble="enfilade"]';
      const boite = await page.locator(enfilade).boundingBox();
      // l'enfilade sous la bande des étagères : côté pièce
      await page.click(enfilade, {position: {x: boite.width * 0.85, y: boite.height / 2}});
      f = await fiche();
      const ouverte = f => f.hash === "#plan?k=enfilade" && f.nom.includes("Enfilade") && f.liens.includes("Coupe A")
        && f.liens.includes("Iso") && f.ici === 1 && f.corps.includes("Contre le mur ouest");
      verifier(ouverte(f), `${t}, toucher l'enfilade : ${JSON.stringify(f)}`);
      await page.click('section[data-vue="plan"] .fiche-meuble button:text-is("Fermer")');
      await page.focus(enfilade);
      await page.keyboard.press("Enter");
      f = await fiche();
      verifier(ouverte(f), `${t}, Entrée sur l'enfilade : ${JSON.stringify(f)}`);
      await ouvrir(page, DOC + "#plan?k=enfilade");
      await attendre(page, () => document.querySelectorAll('section[data-vue="plan"] rect.zone.ici').length === 1, null,
                     `${t} : #plan?k=enfilade n'ouvre pas la fiche`);
      f = await fiche();
      verifier(ouverte(f), `${t}, #plan?k=enfilade : ${JSON.stringify(f)}`);
    }
    // chaque meuble, touché au centre de sa partie visible, ouvre sa fiche et aucune autre
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plan");
    const cs = await cibles();
    verifier(egal(cs.map(c => c.id), ZONES), `plan : zones visibles ${JSON.stringify(cs.map(c => c.id))}`);
    for (const c of cs) {
      if (!c.n) { echecs.push(`plan, ${c.id} : aucun point visible`); continue; }
      await page.mouse.click(c.x, c.y);
      const r = await page.evaluate(() => ({hash: location.hash,
        ici: [...document.querySelectorAll('section[data-vue="plan"] rect.zone.ici')].map(z => z.dataset.meuble)}));
      verifier(r.hash === `#plan?k=${c.id}` && egal(r.ici, [c.id]),
               `plan, toucher ${c.id} en son centre visible : ${JSON.stringify(r)}`);
    }
    // la fiche de la table suit l'option Table : au quotidien la ronde, ouverte l'ovale
    await ouvrir(page, DOC + "#plan?k=table");
    await attendre(page, () => document.querySelectorAll('section[data-vue="plan"] rect.zone.ici').length === 1, null, "plan : #plan?k=table");
    let f = await fiche();
    verifier(f.corps.includes("100 × 100") && f.corps.includes("ronde") && !f.corps.includes("ovale"), `table au quotidien : ${JSON.stringify(f)}`);
    await choisir(page, "table", "ouverte");
    f = await fiche();
    verifier(f.corps.includes("280 × 100") && f.corps.includes("ovale de 280"), `table ouverte : ${JSON.stringify(f)}`);
    await page.evaluate(() => localStorage.clear());
    const barre = await page.evaluate(() => ({
      comparer: [...document.querySelectorAll("#c-comp")].filter(b => b.checkVisibility()).length,
      perso: [...document.querySelectorAll("#c-options")].filter(b => b.checkVisibility()).length}));
    verifier(barre.comparer === 0 && barre.perso === 1, `barre : ${JSON.stringify(barre)}`);
  });

  // ------------------------------------------------------------------ Personnaliser : options « choix »
  const ORIGINE = "table:quotidien siege:dyvlinge deco:masquee bois:chene";
  // jetons des éléments marqués visibles dans la vue (display calculé : checkVisibility ne le voit pas sur du SVG)
  const montres = (p, vue) => p.evaluate(v => {
    const vu = e => { for (let x = e; x; x = x.parentElement) if (getComputedStyle(x).display === "none") return false; return true; };
    const jetons = new Set();
    for (const e of document.querySelectorAll(`section[data-vue="${v}"] .scene [data-si]`))
      if (vu(e)) for (const j of e.dataset.si.split(" ")) jetons.add(j);
    return {options: document.documentElement.dataset.options, jetons: [...jetons].sort(),
            images: [...document.querySelectorAll(`section[data-vue="${v}"] .scene img`)].filter(vu).map(i => i.getAttribute("src"))};
  }, vue);
  await partie("personnaliser", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plan");
    await page.evaluate(() => localStorage.clear());
    await ouvrir(page, DOC + "#plan");
    let m = await montres(page, "plan");
    verifier(m.options === ORIGINE && egal(m.jetons, ["siege:dyvlinge", "table:quotidien"]), `origine, plan : ${JSON.stringify(m)}`);
    const cas = [
      ["plan", "table", "ouverte", ["siege:dyvlinge", "table:ouverte"]],
      ["plan", "siege", "chilienne", ["siege:chilienne", "table:ouverte"]],
      ["plan", "table", "quotidien", ["siege:chilienne", "table:quotidien"]],
      ["plan", "deco", "affichee", ["deco:affichee", "siege:chilienne", "table:quotidien"]],
      ["coupes?k=A", "deco", "affichee", ["deco:affichee", "siege:chilienne"]],
      ["coupes?k=C", "table", "ouverte", ["deco:affichee", "siege:chilienne", "table:ouverte"]],
      ["coupes?k=D", "siege", "dyvlinge", ["deco:affichee", "siege:dyvlinge", "table:ouverte"]],
      ["coupes?k=B", "deco", "masquee", ["table:ouverte"]],
    ];
    for (const [adresse, o, code, attendu] of cas) {
      await ouvrir(page, `${DOC}#${adresse}`);
      const vue = adresse.split("?")[0];
      const avant = await page.evaluate(v => document.querySelector(`section[data-vue="${v}"] .scene`).innerHTML.length, vue);
      await choisir(page, o, code);
      m = await montres(page, vue);
      // les jetons du dessin sont un sous-ensemble de l'état choisi : ce que montre la vue n'a que des éléments de cet état
      verifier(m.options.includes(`${o}:${code}`) && m.jetons.every(j => m.options.split(" ").includes(j)),
               `${o} = ${code}, ${adresse} : ${JSON.stringify(m)}`);
      verifier(await page.evaluate(([v, a]) => document.querySelector(`section[data-vue="${v}"] .scene`).innerHTML.length === a,
                                   [vue, avant]), `${o} = ${code} : la scène a été réécrite au lieu d'être filtrée`);
    }
    // l'état atteint tient au rechargement
    await ouvrir(page, DOC + "#plan");
    m = await montres(page, "plan");
    verifier(m.options === "table:ouverte siege:dyvlinge deco:masquee bois:chene" && egal(m.jetons, ["siege:dyvlinge", "table:ouverte"]),
             `après rechargement : ${JSON.stringify(m)}`);
    // Bois : une image par valeur, la vue Iso montre celle du choix
    await ouvrir(page, DOC + "#iso?k=se");
    m = await montres(page, "iso");
    verifier(egal(m.images, ["rendus/iso_se.jpg"]), `iso SE, chêne : ${JSON.stringify(m.images)}`);
    await choisir(page, "bois", "noyer");
    m = await montres(page, "iso");
    verifier(egal(m.images, ["rendus/iso_se-noyer.jpg"]), `iso SE, noyer : ${JSON.stringify(m.images)}`);
    await ouvrir(page, DOC + "#iso?k=no");
    m = await montres(page, "iso");
    verifier(egal(m.images, ["rendus/iso_no-noyer.jpg"]), `iso NO, noyer : ${JSON.stringify(m.images)}`);
    await imagesChargees(page, "iso");
    // Valeurs d'origine
    await page.click("#c-options");
    await page.click("#panneau-options >> text=Valeurs d'origine");
    await page.keyboard.press("Escape");
    m = await montres(page, "iso");
    verifier(m.options === ORIGINE && egal(m.images, ["rendus/iso_no.jpg"]), `valeurs d'origine : ${JSON.stringify(m)}`);
    await page.evaluate(() => localStorage.clear());

    // sans localStorage : les défauts, sans erreur
    const prive = await page.context().browser().newContext();
    try {
      await sansPolices(prive);
      await prive.addInitScript(() => {
        const refus = () => { throw new DOMException("stockage refusé", "SecurityError"); };
        Storage.prototype.getItem = refus;
        Storage.prototype.setItem = refus;
      });
      const p = await prive.newPage();
      await preparer(p);
      await p.goto(DOC + "#plan");
      m = await montres(p, "plan");
      verifier(m.options === ORIGINE && egal(m.jetons, ["siege:dyvlinge", "table:quotidien"]), `sans localStorage : ${JSON.stringify(m)}`);
    } finally {
      await prive.close();
    }
  });

  // ------------------------------------------------------------------ dessins : pas de noir, texte dans le viewBox
  await partie("dessins", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC);
    await page.evaluate(() => localStorage.clear());
    const html = await page.evaluate(async u => (await fetch(u)).text(), DOC);
    const verifierDessins = async (etat) => {
      for (const adresse of ["plan", "coupes?k=A", "coupes?k=B", "coupes?k=C", "coupes?k=D"]) {
        const t = `dessins, ${etat}, ${adresse}`;
        await ouvrir(page, `${DOC}#${adresse}`);
        const vue = adresse.split("?")[0];
        await attendre(page, a => { const e = document.querySelector(`section[data-vue="${a.v}"] .scene > .element${a.k ? `[data-k="${a.k}"]` : ""}`);
                                    return e && e.checkVisibility(); }, {v: vue, k: adresse.split("=")[1] || ""}, `${t} : rien ne s'affiche`);
        const r = await page.evaluate(([v, source]) => {
          const vu = e => { for (let x = e; x; x = x.parentElement) if (getComputedStyle(x).display === "none") return false; return true; };
          const SEL = ".scene > .element > svg";
          const section = document.querySelector(`section[data-vue="${v}"]`);
          const d0 = new DOMParser().parseFromString(source, "text/html").querySelector(`section[data-vue="${v}"]`);
          const tous = [...section.querySelectorAll(SEL)], origine = [...d0.querySelectorAll(SEL)];
          const noirs = [], dehors = [], svgs = tous.filter(s => s.checkVisibility());
          for (const svg of svgs) {
            const [x0, y0, w, h] = origine[tous.indexOf(svg)].getAttribute("viewBox").trim().split(/[\s,]+/).map(Number);
            for (const e of svg.querySelectorAll("path,rect,circle,ellipse,polygon,polyline,text,tspan")) {
              if (e.closest("defs,clipPath,marker,mask,symbol") || !vu(e)) continue;
              if (getComputedStyle(e).fill === "rgb(0, 0, 0)") noirs.push(`${e.tagName}${e.getAttribute("class") ? "." + e.getAttribute("class") : ""}`);
            }
            const versSvg = svg.getScreenCTM().inverse();
            for (const tx of svg.querySelectorAll("text")) {
              if (!vu(tx) || !tx.textContent.trim() || tx.closest(".trace-mesure")) continue;
              const b = tx.getBBox(), m = versSvg.multiply(tx.getScreenCTM());
              const pts = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]].map(([x, y]) => {
                const p = svg.createSVGPoint(); p.x = x; p.y = y; return p.matrixTransform(m);
              });
              const g = 0.5;
              if (Math.min(...pts.map(p => p.x)) < x0 - g || Math.max(...pts.map(p => p.x)) > x0 + w + g
                  || Math.min(...pts.map(p => p.y)) < y0 - g || Math.max(...pts.map(p => p.y)) > y0 + h + g)
                dehors.push(tx.textContent.trim().slice(0, 30));
            }
          }
          return {n: svgs.length, noirs, dehors};
        }, [vue, html]);
        verifier(r.n > 0, `${t} : aucun dessin visible`);
        verifier(r.noirs.length === 0, `${t} : aplat noir ${JSON.stringify(r.noirs.slice(0, 8))}`);
        verifier(r.dehors.length === 0, `${t} : texte hors du viewBox ${JSON.stringify(r.dehors.slice(0, 8))}`);
      }
    };
    await verifierDessins("origine");
    await ouvrir(page, DOC + "#plan");
    await choisir(page, "table", "ouverte");
    await choisir(page, "siege", "chilienne");
    await choisir(page, "deco", "affichee");
    await verifierDessins("table ouverte, chilienne, déco");
    await page.evaluate(() => localStorage.clear());
  });

  // ------------------------------------------------------------------ Explication
  await partie("explication", async () => {
    for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
      await page.setViewportSize({width: largeur, height: hauteur});
      await ouvrir(page, DOC + "#explication");
      await attendre(page, () => document.querySelector('section[data-vue="explication"]').checkVisibility(), null, "explication : ne s'affiche pas");
      const e = await page.evaluate(() => {
        const s = document.querySelector('section[data-vue="explication"]');
        return {cartes: s.querySelectorAll("ol.principes > li").length,
                titres: [...s.querySelectorAll("h2")].map(h => h.textContent),
                tableaux: s.querySelectorAll("table").length,
                montrer: [...s.querySelectorAll("ol.principes a")].filter(a => /plan/.test(a.getAttribute("href") || "")).length,
                liens: [...s.querySelectorAll("a")].map(a => a.getAttribute("href")).filter(h => h === "../etageres/" || h === "../enfilade/")};
      });
      verifier(e.cartes === 17, `${largeur} px, explication : ${e.cartes} cartes au lieu de 17`);
      verifier(egal(e.titres, ["Principe", "Matériaux", "Pistes déco", "Rangements", "Tables qui se replient", "Meubles à fabriquer", "Points à vérifier"]),
               `${largeur} px, explication : titres ${JSON.stringify(e.titres)}`);
      verifier(e.tableaux === 3 && e.montrer === 13 && e.liens.length >= 4, `${largeur} px, explication : ${JSON.stringify(e)}`);
      const d = await debordements(page);
      verifier(d.length === 0, `${largeur} px, explication : déborde (${d.join(" ; ")})`);
    }
    // « Montrer sur le plan » ouvre la fiche du meuble
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#explication");
    await page.click('section[data-vue="explication"] ol.principes li:nth-child(3) a');
    await attendre(page, () => location.hash === "#plan?k=canape", null, "explication : « Montrer sur le plan » du canapé");
    // les liens vers les deux meubles répondent
    const statuts = await page.evaluate(async b => Promise.all(["/salon/etageres/", "/salon/enfilade/"].map(u => fetch(b + u).then(x => x.status))), BASE);
    verifier(egal(statuts, [200, 200]), `explication : liens des meubles ${JSON.stringify(statuts)}`);
  });

  // ------------------------------------------------------------------ anciennes adresses
  await partie("anciennes adresses", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    const suivre = async (entree, chemin) => {
      await page.goto("about:blank");
      await page.goto(BASE + entree);
      await attendre(page, c => location.pathname === c && document.readyState === "complete", chemin, `${entree} : n'arrive pas à ${chemin}`);
      return page.evaluate(() => ({chemin: location.pathname, hash: location.hash,
        vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue)}));
    };
    const cas = [
      ["/salon-v4.html", "/salon/amenagement/", ["", "#plan"], ["plan"]],
      ["/salon-v4.html#plan", "/salon/amenagement/", ["#plan"], ["plan"]],
      ["/salon-v4.html#coupe-a-a-mur-ouest", "/salon/amenagement/", ["#coupes?k=A"], ["coupes"]],
      ["/salon-v4.html#coupe-b-b-baie-et-desserte", "/salon/amenagement/", ["#coupes?k=B"], ["coupes"]],
      ["/salon-v4.html#coupe-c-c-a-travers-la-table", "/salon/amenagement/", ["#coupes?k=C"], ["coupes"]],
      ["/salon-v4.html#coupe-d-d-mur-sud-ecran", "/salon/amenagement/", ["#coupes?k=D"], ["coupes"]],
      ["/salon-v4.html#rendu-3d", "/salon/amenagement/", ["#iso"], ["iso"]],
      ["/salon-v4.html#materiaux", "/salon/amenagement/", ["#explication"], ["explication"]],
      ["/salon-v4.html#tables-qui-se-replient", "/salon/amenagement/", ["#explication"], ["explication"]],
      ["/salon-v4.html#meubles", "/salon/amenagement/", ["#explication"], ["explication"]],
      ["/salon-v4.html#points-a-verifier", "/salon/amenagement/", ["#explication"], ["explication"]],
      ["/salon-v4.html#inconnue", "/salon/amenagement/", ["", "#plan"], ["plan"]],
      ["/salon-v4.html#changements", "/salon/amenagement/historique.html", [""], null],
    ];
    for (const [entree, chemin, hashs, vues] of cas) {
      const r = await suivre(entree, chemin);
      verifier(r.chemin === chemin && hashs.includes(r.hash) && (vues === null || egal(r.vues, vues)),
               `${entree} : ${JSON.stringify(r)} au lieu de ${chemin}${hashs[hashs.length - 1]}`);
    }
    // les liens des deux meubles vers le salon : la nouvelle adresse, sans passer par la redirection
    for (const meuble of ["/salon/etageres/", "/salon/enfilade/"]) {
      await ouvrir(page, BASE + meuble + "#explication");
      const liens = await page.evaluate(() => [...document.querySelectorAll("a")].map(a => a.getAttribute("href")).filter(h => /salon-v4|amenagement/.test(h || "") && !(h || "").startsWith("../../")));
      verifier(liens.length > 0 && liens.every(h => h === "../amenagement/"), `${meuble} : liens vers le salon ${JSON.stringify(liens)}`);
    }
  });

  // ------------------------------------------------------------------ historique
  await partie("historique", async () => {
    await ouvrir(page, DOC + "historique.html");
    const h = await page.evaluate(() => ({
      figees: [...document.querySelectorAll("ul.figees li")].map(li => li.textContent.trim().split(" ")[0]),
      liens: [...document.querySelectorAll("ul.figees a")].map(a => a.href),
      journaux: [...document.querySelectorAll("ol.fil")].map(o => o.children.length),
      premiere: (document.querySelector("ol.fil li") || {textContent: ""}).textContent,
    }));
    verifier(egal(h.figees, ["V3.1", "V2.1", "V1"]), `historique : versions figées ${JSON.stringify(h.figees)}`);
    verifier(egal(h.journaux, [28]), `historique : changements ${JSON.stringify(h.journaux)}`);
    verifier(h.premiere.includes("V4.26"), `historique : la première entrée n'est pas V4.26 : « ${h.premiere.slice(0, 60)} »`);
    const statuts = await page.evaluate(liens => Promise.all(liens.map(l => fetch(l).then(x => x.status))), h.liens);
    verifier(statuts.length === 3 && statuts.every(s => s === 200), `historique : versions figées introuvables ${JSON.stringify(statuts)}`);
  });

  // ------------------------------------------------------------------ sans JavaScript
  await partie("sans JavaScript", async () => {
    const sansJs = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      await sansPolices(sansJs);
      const p = await sansJs.newPage();
      await preparer(p);
      for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
        await p.setViewportSize({width: largeur, height: hauteur});
        await p.goto(DOC);
        const s = await p.evaluate(() => ({
          classe: document.documentElement.className,
          vues: [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility()).map(x => x.dataset.vue),
          principes: [...document.querySelectorAll("ol.principes > li")].filter(x => x.checkVisibility()).length,
          // l'état d'origine sans script : la table ouverte, le siège chilienne et la déco n'apparaissent pas
          ouverts: [...document.querySelectorAll('section[data-vue="plan"] .scene [data-si]')].filter(e => {
            for (let x = e; x; x = x.parentElement) if (getComputedStyle(x).display === "none") return false; return true;
          }).map(e => e.dataset.si).filter(j => /ouverte|chilienne|affichee/.test(j)).length,
        }));
        verifier(s.classe.includes("sans-js") && s.principes > 0 && s.vues.includes("plan") && s.vues.includes("explication")
                 && s.ouverts === 0,
                 `sans JavaScript, ${largeur} px : ${JSON.stringify(s)}`);
        const d = await debordements(p);
        verifier(!d.some(x => x.startsWith("page")), `sans JavaScript, ${largeur} px : déborde (${d.join(" ; ")})`);
      }
    } finally {
      await sansJs.close();
    }
  });

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
