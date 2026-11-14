/* @site reel : la chambre sur le vrai site/, construit par python3 site.py (tests/navigateur/lancer.sh le sert).
   - Vues : les cinq vues et les trois élévations, à 1440, 1100 et 390 px : sans erreur de console ni réponse en
     erreur, rien ne déborde ; Plan, Coupes, Explication actives ; Iso et Caméra grisées, « Pas encore rendu ».
   - Pas de comparaison : une seule variante, ni choix de variante ni « Comparer » dans la barre.
   - Plan : toucher le lit ouvre sa fiche (« Coupe sud »), la touche Entrée aussi ; un calque masqué (Cotes,
     Passages libres) masque tous ses éléments.
   - Position : sur chaque élévation, seul son trait de coupe est marqué sur le mini-plan.
   - Dessins lisibles : aucune forme noire par défaut de style, aucune étiquette hors de son dessin.
   - Anciennes adresses, historique (une version figée, un journal de 5 lignes), accueil, page sans JavaScript. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/chambre/amenagement/`;
  const VUES = ["plan", "coupes", "iso", "camera", "explication"];
  const GRISEES = ["iso", "camera"];
  const ELEVATIONS = ["est", "sud", "ouest"];
  const LARGEURS = [[1440, 900], [1100, 800], [390, 844]];
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };
  const egal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  const preparer = async p => {
    p.on("console", m => { if (m.type() === "error") erreurs.push(`console : ${m.text()}`); });
    p.on("pageerror", e => erreurs.push(`page : ${e.message}`));
    p.on("response", r => { if (r.status() >= 400) erreurs.push(`${r.status()} : ${r.url()}`); });
    p.on("requestfailed", r => {   // une requête interrompue par le changement de page n'est pas une erreur du site
      const raison = (r.failure() || {}).errorText || "";
      if (!raison.includes("ERR_ABORTED")) erreurs.push(`échec : ${r.url()} (${raison})`);
    });
    p.setDefaultTimeout(3000);
    await p.emulateMedia({reducedMotion: "reduce"});
  };
  // polices de Google : feuille vide, le test ne dépend pas du réseau
  const sansPolices = ctx => ctx.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                                       r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  const ouvrir = async (p, adresse) => { await p.goto("about:blank"); await p.goto(adresse); };
  const attendre = async (p, condition, arg, message) => {
    try { await p.waitForFunction(condition, arg, {timeout: 3000}); return true; } catch (e) { echecs.push(message); return false; }
  };

  // Ce qui dépasse : la page en largeur ; la barre, les onglets, la scène, la fiche hors de l'écran ; un contenu plus
  // large que sa boîte (barre, fiche, article de lecture). Les tableaux sont dans .defile, qui défile exprès.
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

  // Dessins de la scène visible : formes noires (l'encre du site est #1D2A33, un noir pur vient d'un style oublié),
  // et textes dont la boîte, ramenée dans le repère du SVG (rotations comprises), sort de son viewBox.
  const illisibles = (p, vue) => p.evaluate(v => {
    const res = [], noir = "rgb(0, 0, 0)";
    const section = document.querySelector(`section[data-vue="${v}"]`);
    const formes = [...section.querySelectorAll(".scene svg :is(rect, path, circle, line, text)")].filter(x => x.checkVisibility());
    // un fill ne peint rien sur une ligne ni sur un chemin de deux points (le tiret des cotes, path.tkm, « M2 8 L8 2 »)
    const sansSurface = x => x.tagName === "line" ||
      (x.tagName === "path" && (x.getAttribute("d").match(/-?\d*\.?\d+/g) || []).length <= 4);
    for (const x of formes) {
      const s = getComputedStyle(x);
      if ((s.fill === noir && !sansSurface(x)) || s.stroke === noir) res.push(`${x.tagName} ${x.getAttribute("class") || ""} : fill ${s.fill}, stroke ${s.stroke}`);
    }
    for (const t of formes.filter(x => x.tagName === "text")) {
      const svg = t.ownerSVGElement, vb = svg.viewBox.baseVal, b = t.getBBox();
      if (!vb || !vb.width) continue;
      const m = svg.getScreenCTM().inverse().multiply(t.getScreenCTM());
      const coins = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]]
        .map(([x, y]) => new DOMPoint(x, y).matrixTransform(m));
      const xs = coins.map(c => c.x), ys = coins.map(c => c.y);
      if (Math.min(...xs) < vb.x - 0.5 || Math.max(...xs) > vb.x + vb.width + 0.5 ||
          Math.min(...ys) < vb.y - 0.5 || Math.max(...ys) > vb.y + vb.height + 0.5)
        res.push(`« ${t.textContent} » hors du viewBox ${vb.x} ${vb.y} ${vb.width} ${vb.height}`);
    }
    return {n: formes.length, res};
  }, vue);

  // chaque partie est vérifiée même si une autre a levé une exception
  const partie = async (nom, f) => {
    try { await f(); } catch (e) { echecs.push(`${nom} : exception : ${e.message.split("\n")[0]}`); }
  };

  await sansPolices(page.context());
  await preparer(page);
  await ouvrir(page, DOC);
  await page.evaluate(() => localStorage.clear());

  // ------------------------------------------------------------------ les cinq vues, les trois élévations, trois largeurs
  await partie("vues", async () => {
    for (const [largeur, hauteur] of LARGEURS) {
      await page.setViewportSize({width: largeur, height: hauteur});
      for (const vue of VUES) {
        await ouvrir(page, `${DOC}#${vue}`);
        for (const k of vue === "coupes" ? ELEVATIONS : [""]) {
          const t = `${largeur} px, ${vue}${k ? " " + k : ""}`;
          if (k) {
            await page.evaluate(k => { location.hash = `#coupes?k=${k}`; }, k);
            await attendre(page, k => {
              const e = document.querySelector(`section[data-vue="coupes"] .scene > .element[data-k="${k}"]`);
              return e && e.checkVisibility();
            }, k, `${t} : l'élévation ne s'affiche pas`);
          }
          const e = await page.evaluate(v => {
            const s = document.querySelector(`section[data-vue="${v}"]`), vide = s.querySelector(":scope > .vide");
            return {vues: [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility()).map(x => x.dataset.vue),
                    grise: document.querySelector(`nav.vues a[data-vue="${v}"]`).getAttribute("aria-disabled"),
                    vide: vide && vide.checkVisibility() ? vide.textContent : ""};
          }, vue);
          if (GRISEES.includes(vue))
            verifier(egal(e.vues, [vue]) && e.grise === "true" && e.vide === "Pas encore rendu", `${t} : grisée ${JSON.stringify(e)}`);
          else
            verifier(egal(e.vues, [vue]) && e.grise !== "true" && e.vide === "", `${t} : ${JSON.stringify(e)}`);
          const d = await debordements(page);
          verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
          if (["plan", "coupes"].includes(vue)) {
            const i = await illisibles(page, vue);
            verifier(i.n > 0 && i.res.length === 0, `${t} : dessin illisible (${i.n} formes ; ${i.res.slice(0, 8).join(" ; ")})`);
          }
        }
      }
    }
  });

  // ------------------------------------------------------------------ une seule variante : pas de comparaison
  await partie("pas de comparaison", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    for (const vue of ["plan", "coupes"]) {
      await ouvrir(page, `${DOC}#${vue}`);
      const b = await page.evaluate(() => {
        const barre = document.querySelector("#barre");
        const visibles = [...barre.querySelectorAll("button, select, label, a")].filter(x => x.checkVisibility());
        return {comp: Boolean(document.querySelector("#c-comp, #c-autre, #c-variante")),
                textes: visibles.map(x => x.textContent.trim()).filter(x => /compar|variante/i.test(x))};
      });
      verifier(!b.comp && b.textes.length === 0, `${vue} : comparaison ou choix de variante dans la barre ${JSON.stringify(b)}`);
    }
  });

  // ------------------------------------------------------------------ plan : le lit, au toucher et au clavier ; calques
  const LIT = 'section[data-vue="plan"] rect.zone[data-meuble="lit"]';
  const fiche = () => page.evaluate(() => {
    const s = document.querySelector('section[data-vue="plan"]');
    return {hash: location.hash, nom: s.querySelector(".fiche-nom").textContent,
            liens: [...s.querySelectorAll(".fiche-meuble a, .fiche-meuble button")].map(a => a.textContent.trim()),
            corps: s.querySelector(".fiche-meuble").textContent, ici: s.querySelectorAll("rect.zone.ici").length};
  });
  await partie("plan", async () => {
    const ouverte = f => f.hash === "#plan?k=lit" && f.nom.includes("① Lit 160, tête au sud") && f.liens.includes("Coupe sud") && f.ici === 1;
    for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
      const t = `${largeur} px, plan`;
      await page.setViewportSize({width: largeur, height: hauteur});
      await ouvrir(page, DOC + "#plan");
      await page.click(LIT);
      let f = await fiche();
      verifier(ouverte(f), `${t}, toucher le lit : ${JSON.stringify(f)}`);
      await page.click('section[data-vue="plan"] .fiche-meuble button:text-is("Fermer")');
      f = await fiche();
      verifier(f.hash === "#plan" && f.ici === 0 && f.corps.includes("Touchez un meuble"), `${t}, Fermer : ${JSON.stringify(f)}`);
      await page.focus(LIT);
      await page.keyboard.press("Enter");
      f = await fiche();
      verifier(ouverte(f), `${t}, Entrée sur le lit : ${JSON.stringify(f)}`);
    }

    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plan");
    const vus = sel => page.evaluate(s => {
      const xs = [...document.querySelectorAll(`section[data-vue="plan"] .scene :is(${s})`)];
      return {n: xs.length, vus: xs.filter(x => x.checkVisibility()).length};
    }, sel);
    for (const [calque, nom, sel] of [["cotes", "Cotes", ".dim,.dimt"], ["passages", "Passages libres", ".pass,.passm,.passt"]]) {
      const bouton = `section[data-vue="plan"] .calques button[data-calque="${calque}"]`;
      const avant = await vus(sel);
      await page.click(bouton);
      const apres = await vus(sel);
      const presse = await page.getAttribute(bouton, "aria-pressed");
      verifier(avant.n > 0 && avant.vus === avant.n && apres.vus === 0 && presse === "false",
               `calque ${nom} : avant ${JSON.stringify(avant)}, masqué ${JSON.stringify(apres)}, aria-pressed ${presse}`);
      await page.click(bouton);
      const remis = await vus(sel);
      verifier(remis.vus === avant.n, `calque ${nom} remis : ${JSON.stringify(remis)}`);
    }
    await page.evaluate(() => localStorage.clear());
  });

  // ------------------------------------------------------------------ « Position » : l'élévation affichée, sur le mini-plan
  await partie("position", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    for (const k of ELEVATIONS) {
      await ouvrir(page, `${DOC}#coupes?k=${k}`);
      await attendre(page, k => {
        const x = document.querySelector(`section[data-vue="coupes"] .mini line.sec[data-k="${k}"]`);
        return Boolean(x && x.classList.contains("ici"));
      }, k, `Position, ${k} : son trait n'est pas marqué`);
      const ici = await page.evaluate(() => [...document.querySelectorAll('section[data-vue="coupes"] .mini line.sec')]
        .filter(x => x.classList.contains("ici")).map(x => x.dataset.k));
      verifier(egal(ici, [k]), `Position, ${k} : traits marqués ${JSON.stringify(ici)}`);
    }
  });

  // ------------------------------------------------------------------ anciennes adresses
  await partie("anciennes adresses", async () => {
    const suivre = async (entree, chemin) => {
      await page.goto("about:blank");
      await page.goto(BASE + entree);
      await attendre(page, c => location.pathname === c && document.readyState === "complete", chemin, `${entree} : n'arrive pas à ${chemin}`);
      return page.evaluate(() => ({chemin: location.pathname, hash: location.hash,
        vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue)}));
    };
    const ANC = "/chambre-amenagement.html", CIBLE = "/chambre/amenagement/";
    let r = await suivre(ANC, CIBLE);
    verifier(r.hash === "" && egal(r.vues, ["plan"]), `ancienne page : ${JSON.stringify(r)}`);
    for (const [ancre, vue] of [["verifier", "explication"], ["elevations", "coupes"], ["plan-a-l-echelle", "plan"],
                                ["principe", "explication"]]) {
      r = await suivre(`${ANC}#${ancre}`, CIBLE);
      verifier(r.hash === `#${vue}` && egal(r.vues, [vue]), `ancienne ancre « ${ancre} » : ${JSON.stringify(r)}`);
    }
    r = await suivre(`${ANC}#inconnue`, CIBLE);
    verifier(r.hash === "" && egal(r.vues, ["plan"]), `ancienne ancre inconnue : ${JSON.stringify(r)}`);
    r = await suivre(`${ANC}#changements`, CIBLE + "historique.html");
    verifier(r.chemin === CIBLE + "historique.html" && r.hash === "", `ancienne ancre « changements » : ${JSON.stringify(r)}`);
  });

  // ------------------------------------------------------------------ historique
  await partie("historique", async () => {
    await ouvrir(page, DOC + "historique.html");
    const h = await page.evaluate(() => ({
      figees: [...document.querySelectorAll("ul.figees li")].map(li => li.textContent.trim()),
      liens: [...document.querySelectorAll("ul.figees a")].map(a => a.href),
      journaux: [...document.querySelectorAll("ol.fil")].map(o => o.children.length),
    }));
    verifier(egal(h.figees, ["V1.2 4 octobre 2026"]), `historique : versions figées ${JSON.stringify(h.figees)}`);
    verifier(egal(h.journaux, [5]), `historique : journaux ${JSON.stringify(h.journaux)}`);
    const statuts = await page.evaluate(liens => Promise.all(liens.map(l => fetch(l).then(x => x.status))), h.liens);
    verifier(egal(statuts, [200]), `historique : version figée introuvable ${JSON.stringify(statuts)}`);
  });

  // ------------------------------------------------------------------ accueil
  await partie("accueil", async () => {
    await ouvrir(page, BASE + "/");
    const a = await page.evaluate(() => {
      const lien = document.querySelector('svg.plan-appart a[aria-label="Chambre"]');
      const noms = [...document.querySelectorAll("svg.plan-appart text.pl-nom")];
      const nom = noms.find(t => t.textContent === "Chambre");
      const cote = nom && nom.nextElementSibling;
      return {href: lien && lien.getAttribute("href"), cote: cote && cote.classList.contains("pl-cote") ? cote.textContent : ""};
    });
    verifier(a.href === "chambre/amenagement/" && a.cote === "10,3 m²", `accueil : ${JSON.stringify(a)}`);
    await page.click('svg.plan-appart a[aria-label="Chambre"]');
    await attendre(page, () => location.pathname === "/chambre/amenagement/", null, "accueil : la chambre ne mène pas à sa page");
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
          vues: [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility())
            .map(x => { const r = x.getBoundingClientRect(); return [x.dataset.vue, Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; }),
        }));
        const suite = s.vues.every((v, i) => i === 0 || v[1] >= s.vues[i - 1][2] - 1);
        verifier(s.classe.includes("sans-js") && egal(s.vues.map(v => v[0]), VUES) && suite,
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
