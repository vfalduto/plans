/* @site reel : la cuisine/aménagement sur le vrai site/, construit par python3 site.py (tests/navigateur/lancer.sh).
   - Vues : chaque vue et chaque repère à 1440, 1100 et 390 px : sans erreur de console ni réponse en erreur, images
     chargées, rien ne déborde ; « Position » marque l'élément affiché ; Iso : NE et SE grisés.
   - Plan : toucher B3 ouvre sa fiche (« Coupe A », « Iso »), la touche Entrée aussi ; #plan?k=b3 l'ouvre ; à 1440,
     chaque meuble touché au centre de sa partie visible ouvre sa propre fiche ;
     #plan?k=elec montre le plan électrique sans fiche de meuble. Pas de « Comparer » (une seule variante).
   - Personnaliser : Taille, Porte d'entrée, Porte du cellier, transparence de la coupe C ; chaque valeur change le
     dessin, « Valeurs d'origine » revient, le choix tient au rechargement ; sans localStorage, les défauts.
   - Anciennes adresses (cuisine-v13.html et ses ancres, imprimable, maquette : modele.js sans 404 ; three.js, chargé
     depuis jsdelivr, est remplacé par des modules vides : la maquette ne tourne pas, seules les réponses comptent).
   - Historique (versions figées V11.49 et V12.7, 90 changements) et la page sans JavaScript. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/cuisine/amenagement/`;
  const VUES = ["plan", "coupes", "iso", "camera", "explication"];
  const LARGEURS = [[1440, 900], [1100, 800], [390, 844]];
  const REPERES = {plan: ["", "elec"], coupes: ["A", "B", "C", "elec"], iso: ["no", "so", "so-nuit"],
                   camera: ["entree", "fenetre", "banquette", "dos_cellier", "cellier"], explication: [""]};
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
    const boites = [["barre", document.querySelector("#barre")], ["onglets", document.querySelector("nav.vues")]];
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
    .filter(i => i.checkVisibility()).every(i => i.complete && i.naturalWidth > 0), vue, `${vue} : image non chargée`);
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
        const attendus = REPERES[vue].filter(k => k !== "" || vue === "plan");
        verifier(vue === "explication" ? ks.length === 0 : egal(ks, attendus), `${largeur} px, ${vue} : repères ${JSON.stringify(ks)}`);
        if (vue === "iso") {
          const gris = await page.evaluate(() => [...document.querySelectorAll(
            'section[data-vue="iso"] .segments button[data-k]:disabled')].map(b => b.dataset.k));
          verifier(egal(gris, ["ne", "se"]), `${largeur} px, iso : grisés ${JSON.stringify(gris)}`);
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
          if (k && ["coupes", "iso", "camera"].includes(vue)) {
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

  // ------------------------------------------------------------------ plan : B3, le plan électrique
  const B3 = 'section[data-vue="plan"] rect.zone[data-meuble="b3"]';
  const fiche = () => page.evaluate(() => {
    const s = document.querySelector('section[data-vue="plan"]');
    const elec = s.querySelector('.scene > .element[data-k="elec"]');
    return {hash: location.hash, nom: s.querySelector(".fiche-nom").textContent,
            liens: [...s.querySelectorAll(".fiche-meuble a")].map(a => a.textContent),
            corps: s.querySelector(".fiche-meuble").textContent, ici: s.querySelectorAll("rect.zone.ici").length,
            elec: Boolean(elec && elec.checkVisibility())};
  });
  await partie("plan", async () => {
    const ouverte = f => f.hash === "#plan?k=b3" && f.nom.includes("B3") && f.liens.includes("Coupe A")
      && f.liens.includes("Iso") && f.ici === 1 && !f.elec;
    for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
      const t = `${largeur} px, plan`;
      await page.setViewportSize({width: largeur, height: hauteur});
      await ouvrir(page, DOC + "#plan");
      let f = await fiche();
      verifier(f.corps.includes("Touchez un meuble pour afficher sa fiche."), `${t} : invite ${JSON.stringify(f)}`);
      // le bas du meuble : côté mur, B3 est sous la bande murale du meuble haut H2, posée par-dessus
      const boite = await page.locator(B3).boundingBox();
      await page.click(B3, {position: {x: boite.width / 2, y: boite.height * 0.85}});
      f = await fiche();
      verifier(ouverte(f), `${t}, toucher B3 : ${JSON.stringify(f)}`);
      await page.click('section[data-vue="plan"] .fiche-meuble button:text-is("Fermer")');
      await page.focus(B3);
      await page.keyboard.press("Enter");
      f = await fiche();
      verifier(ouverte(f), `${t}, Entrée sur B3 : ${JSON.stringify(f)}`);
      await ouvrir(page, DOC + "#plan?k=b3");
      await attendre(page, () => document.querySelectorAll('section[data-vue="plan"] rect.zone.ici').length === 1, null,
                     `${t} : #plan?k=b3 n'ouvre pas la fiche`);
      f = await fiche();
      verifier(ouverte(f), `${t}, #plan?k=b3 : ${JSON.stringify(f)}`);
      await ouvrir(page, DOC + "#plan?k=elec");
      await attendre(page, () => { const e = document.querySelector('section[data-vue="plan"] .scene > .element[data-k="elec"]');
                                   return e && e.checkVisibility(); }, null, `${t} : #plan?k=elec ne montre pas le plan électrique`);
      f = await fiche();
      verifier(f.elec && f.ici === 0 && !f.liens.includes("Coupe A"), `${t}, #plan?k=elec : ${JSON.stringify(f)}`);
    }
    // chaque meuble, touché au centre de sa partie visible : le point de la zone, non couvert par une zone posée
    // par-dessus, le plus proche du centre de ces points ; il ouvre la fiche de ce meuble et d'aucun autre
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plan");
    const cibles = await page.evaluate(() => {
      const s = document.querySelector('section[data-vue="plan"]');
      return [...s.querySelectorAll("rect.zone[data-meuble]")].filter(z => z.checkVisibility()).map(z => {
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
    verifier(cibles.length === 26, `plan : ${cibles.length} zones visibles, 26 attendues (MEUBLES_PLAN)`);
    for (const c of cibles) {
      if (!c.n) { echecs.push(`plan, ${c.id} : aucun point visible`); continue; }
      await page.mouse.click(c.x, c.y);
      const r = await page.evaluate(() => ({hash: location.hash,
        ici: [...document.querySelectorAll('section[data-vue="plan"] rect.zone.ici')].map(z => z.dataset.meuble)}));
      verifier(r.hash === `#plan?k=${c.id}` && egal(r.ici, [c.id]),
               `plan, toucher ${c.id} en son centre visible : ${JSON.stringify(r)}`);
    }
    const barre = await page.evaluate(() => ({
      comparer: [...document.querySelectorAll("#c-comp")].filter(b => b.checkVisibility()).length,
      perso: [...document.querySelectorAll("#c-options")].filter(b => b.checkVisibility()).length}));
    verifier(barre.comparer === 0 && barre.perso === 1, `barre : ${JSON.stringify(barre)}`);
  });


  // ------------------------------------------------------------------ Personnaliser : options « choix »
  const ORIGINE = "taille:175 porte-entree:fermee porte-cellier:mi-ouverte transparence:oui";
  // les jetons montrés dans la vue (éléments marqués visibles), et l'état posé sur <html>
  // (checkVisibility ne voit pas display:none sur un élément SVG : on remonte les styles calculés)
  const montres = (p, vue) => p.evaluate(v => {
    const vu = e => { for (let x = e; x; x = x.parentElement) if (getComputedStyle(x).display === "none") return false; return true; };
    return {options: document.documentElement.dataset.options,
            vus: [...new Set([...document.querySelectorAll(`section[data-vue="${v}"] .scene [data-si]`)].filter(vu)
              .map(e => e.dataset.si))].sort(),
            etiquettes: [...document.querySelectorAll(`section[data-vue="${v}"] .scene .trp-lbl`)].filter(vu).length};
  }, vue);
  const choisir = async (p, o, code) => {
    await p.click("#c-options");
    await attendre(p, () => document.querySelector("#panneau-options").checkVisibility(), null, "le panneau ne s'ouvre pas");
    await p.click(`#panneau-options section[data-o="${o}"] [data-v="${code}"]`);
    await p.keyboard.press("Escape");
  };
  await partie("personnaliser", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plan");
    await page.evaluate(() => localStorage.clear());
    const cas = [
      ["plan", "porte-entree", "fermee", ["porte-cellier:mi-ouverte", "porte-entree:fermee"]],
      ["plan", "porte-entree", "ouverte", ["porte-cellier:mi-ouverte", "porte-entree:ouverte"]],
      ["plan", "porte-cellier", "fermee", ["porte-cellier:fermee", "porte-entree:ouverte"]],
      ["plan", "porte-cellier", "ouverte", ["porte-cellier:ouverte", "porte-entree:ouverte"]],
      ["coupes?k=A", "taille", "180", ["taille:180"]],
      ["coupes?k=A", "taille", "masquee", []],
      ["coupes?k=C", "transparence", "non", ["transparence:non"]],
    ];
    await ouvrir(page, DOC + "#coupes?k=C");
    let m = await montres(page, "coupes");
    verifier(m.options === ORIGINE && egal(m.vus, ["taille:175", "transparence:oui"]) && m.etiquettes > 0,
             `origine, coupe C : ${JSON.stringify(m)}`);
    for (const [adresse, o, code, attendu] of cas) {
      await ouvrir(page, `${DOC}#${adresse}`);
      const vue = adresse.split("?")[0];
      const avant = await page.evaluate(v => document.querySelector(`section[data-vue="${v}"] .scene`).innerHTML.length, vue);
      await choisir(page, o, code);
      m = await montres(page, vue);
      verifier(egal(m.vus, attendu) && m.options.includes(`${o}:${code}`), `${o} = ${code} : ${JSON.stringify(m)}`);
      if (o === "transparence") verifier(m.etiquettes === 0, `opaque : étiquettes de derrière visibles (${m.etiquettes})`);
      verifier(await page.evaluate(([v, a]) => document.querySelector(`section[data-vue="${v}"] .scene`).innerHTML.length === a,
                                   [vue, avant]), `${o} = ${code} : la scène a été réécrite au lieu d'être filtrée`);
    }
    // le choix tient au rechargement (taille masquée, coupe C opaque)
    await ouvrir(page, DOC + "#coupes?k=C");
    m = await montres(page, "coupes");
    verifier(egal(m.vus, ["transparence:non"]) && m.options === "taille:masquee porte-entree:ouverte porte-cellier:ouverte transparence:non",
             `après rechargement : ${JSON.stringify(m)}`);
    // Valeurs d'origine
    await page.click("#c-options");
    await page.click("#panneau-options >> text=Valeurs d'origine");
    await page.keyboard.press("Escape");
    m = await montres(page, "coupes");
    verifier(m.options === ORIGINE && egal(m.vus, ["taille:175", "transparence:oui"]), `valeurs d'origine : ${JSON.stringify(m)}`);
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
      verifier(m.options === ORIGINE && egal(m.vus, ["porte-cellier:mi-ouverte", "porte-entree:fermee"]),
               `sans localStorage : ${JSON.stringify(m)}`);
    } finally {
      await prive.close();
    }
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
    let r = await suivre("/cuisine-v13.html", "/cuisine/amenagement/");
    verifier(["", "#plan"].includes(r.hash) && egal(r.vues, ["plan"]), `cuisine-v13.html : ${JSON.stringify(r)}`);
    r = await suivre("/cuisine-v13.html#coupe-b-b-mur-sud", "/cuisine/amenagement/");
    verifier(r.hash === "#coupes?k=B" && egal(r.vues, ["coupes"]), `ancienne coupe B : ${JSON.stringify(r)}`);
    r = await suivre("/cuisine-v13.html#electricite", "/cuisine/amenagement/");
    verifier(r.hash === "#plan?k=elec" && egal(r.vues, ["plan"]), `ancienne électricité : ${JSON.stringify(r)}`);
    r = await suivre("/cuisine-v13.html#inconnue", "/cuisine/amenagement/");
    verifier(r.hash === "" && egal(r.vues, ["plan"]), `ancre inconnue : ${JSON.stringify(r)}`);
    r = await suivre("/cuisine-v13.html#changements", "/cuisine/amenagement/historique.html");
    verifier(r.hash === "", `ancienne ancre « changements » : ${JSON.stringify(r)}`);
    r = await suivre("/cuisine-v13.html#V12.7", "/archive/cuisine-v12.7.html");
    verifier(r.chemin === "/archive/cuisine-v12.7.html", `ancienne ancre V12.7 : ${JSON.stringify(r)}`);
    r = await suivre("/cuisine-v13-imprimable.html", "/cuisine/amenagement/imprimable.html");
    verifier(r.chemin === "/cuisine/amenagement/imprimable.html", `ancienne imprimable : ${JSON.stringify(r)}`);
  });

  // ------------------------------------------------------------------ maquette 3D : ses fichiers, sans three.js
  await partie("maquette", async () => {
    const ctx = await page.context().browser().newContext();
    try {
      await sansPolices(ctx);
      await ctx.route(/^https:\/\/cdn\.jsdelivr\.net\//, r => r.fulfill({status: 200, contentType: "text/javascript",
        body: "export class OrbitControls {}; export class GLTFLoader {};"}));
      const p = await ctx.newPage();
      const reponses = [], mauvaises = [];
      p.on("response", r => { reponses.push(r.url()); if (r.status() >= 400) mauvaises.push(`${r.status()} : ${r.url()}`); });
      await p.goto(BASE + "/cuisine-v13-maquette.html");
      await p.waitForFunction(() => location.pathname === "/cuisine/amenagement/maquette-3d.html", null, {timeout: 3000});
      await p.waitForLoadState("load");
      verifier(reponses.some(u => u.endsWith("/cuisine/amenagement/maquette-3d/modele.js")), "maquette : modele.js non chargé");
      verifier(mauvaises.length === 0, `maquette : ${JSON.stringify(mauvaises)}`);
    } finally {
      await ctx.close();
    }
  });

  // ------------------------------------------------------------------ historique
  await partie("historique", async () => {
    await ouvrir(page, DOC + "historique.html");
    const h = await page.evaluate(() => ({
      figees: [...document.querySelectorAll("ul.figees li")].map(li => li.textContent.trim().split(" ")[0]),
      liens: [...document.querySelectorAll("ul.figees a")].map(a => a.href),
      journaux: [...document.querySelectorAll("ol.fil")].map(o => o.children.length),
    }));
    verifier(egal(h.figees, ["V12.7", "V11.49"]), `historique : versions figées ${JSON.stringify(h.figees)}`);
    verifier(egal(h.journaux, [90]), `historique : changements ${JSON.stringify(h.journaux)}`);
    const statuts = await page.evaluate(liens => Promise.all(liens.map(l => fetch(l).then(x => x.status))), h.liens);
    verifier(statuts.length === 2 && statuts.every(s => s === 200), `historique : versions figées introuvables ${JSON.stringify(statuts)}`);
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
        }));
        verifier(s.classe.includes("sans-js") && egal(s.vues, VUES) && s.principes > 0,
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
