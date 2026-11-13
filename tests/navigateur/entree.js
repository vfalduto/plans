/* @site reel : l'entrée sur le vrai site/, construit par python3 site.py (tests/navigateur/lancer.sh le sert).
   - Vues : toutes les vues et tous les repères des deux variantes, à 1440, 1100 et 390 px : sans erreur de console
     ni réponse en erreur (404), images chargées, rien ne déborde de l'écran ni de la fiche.
   - Plan : toucher le banc ouvre sa fiche (« Coupe A »), la touche Entrée aussi ; en comparaison, rien ne s'ouvre.
   - Comparaison : coupe D de Victor face à la principale (« pas d'équivalent »), iso et caméra avec deux rendus.
   - Teinte : « Moka » change --india (dessins) et le filtre des rendus, et se retrouve sur Victor ; à 1440 et 390 px,
     le panneau tient dans l'écran et ses 52 teintes défilent sous son titre et au-dessus de la teinte choisie.
   - Anciennes adresses, historique (versions figées et deux journaux), et la page sans JavaScript. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/entree/amenagement/`;
  const VARIANTES = {principale: DOC, victor: DOC + "victor.html"};
  const VUES = ["plan", "coupes", "iso", "camera", "explication"];
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
  // la comparaison est posée quand le bandeau de la vue a ses deux étiquettes (chargement asynchrone)
  const comparee = (p, vue, message) =>
    attendre(p, v => document.querySelectorAll(`section[data-vue="${v}"] .bandeau .etiq-var`).length === 2, vue, message);
  const etiquettes = (p, vue) => p.evaluate(v =>
    [...document.querySelectorAll(`section[data-vue="${v}"] .bandeau .etiq-var`)].map(e => e.textContent), vue);

  // Ce qui dépasse : la page en largeur ; la barre, les onglets, la scène, la fiche et le panneau hors de l'écran ;
  // un contenu plus large que sa boîte (barre, fiche, article de lecture), donc coupé ou à faire défiler en largeur.
  // Les tableaux sont dans .defile, qui défile en largeur exprès : ils ne comptent pas.
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
  // images visibles de la vue : chargées (complete et une largeur naturelle)
  const imagesChargees = (p, vue) => attendre(p, v => [...document.querySelectorAll(`section[data-vue="${v}"] img`)]
    .filter(i => i.checkVisibility()).every(i => i.complete && i.naturalWidth > 0), vue, `${vue} : image non chargée`);

  // chaque partie est vérifiée même si une autre a levé une exception
  const partie = async (nom, f) => {
    try { await f(); } catch (e) { echecs.push(`${nom} : exception : ${e.message.split("\n")[0]}`); }
  };

  await sansPolices(page.context());
  await preparer(page);

  // ------------------------------------------------------------------ toutes les vues, toutes les largeurs
  await partie("vues", async () => {
    for (const [largeur, hauteur] of LARGEURS) {
      await page.setViewportSize({width: largeur, height: hauteur});
      for (const [variante, adresse] of Object.entries(VARIANTES)) {
        for (const vue of VUES) {
          await ouvrir(page, `${adresse}#${vue}`);
          const ks = await page.evaluate(v => [...document.querySelectorAll(
            `section[data-vue="${v}"] .segments button[data-k]:not(:disabled)`)].map(b => b.dataset.k), vue);
          for (const k of ks.length ? ks : [""]) {
            const t = `${largeur} px, ${variante}, ${vue}${k ? " " + k : ""}`;
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
              grise: document.querySelector(`nav.vues a[data-vue="${v}"]`).getAttribute("aria-disabled"),
            }), vue);
            verifier(egal(e.vues, [vue]) && egal(e.courant, [vue]) && e.grise !== "true", `${t} : ${JSON.stringify(e)}`);
            await imagesChargees(page, vue);
            const d = await debordements(page);
            verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
          }
        }
      }
    }
  });

  // ------------------------------------------------------------------ plan : le banc, au toucher et au clavier
  const BANC = 'section[data-vue="plan"] rect.zone[data-meuble="0"]';
  const fiche = () => page.evaluate(() => {
    const s = document.querySelector('section[data-vue="plan"]');
    return {hash: location.hash, nom: s.querySelector(".fiche-nom").textContent,
            liens: [...s.querySelectorAll(".fiche-meuble a")].map(a => a.textContent),
            corps: s.querySelector(".fiche-meuble").textContent, ici: s.querySelectorAll("rect.zone.ici").length};
  });
  await partie("plan", async () => {
    const ouverte = f => f.hash === "#plan?k=0" && f.nom.includes("Banc") && f.liens.includes("Coupe A") && f.ici === 1;
    for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
      const t = `${largeur} px, plan`;
      await page.setViewportSize({width: largeur, height: hauteur});
      await ouvrir(page, DOC + "#plan");
      await page.click(BANC);
      let f = await fiche();
      verifier(ouverte(f), `${t}, toucher le banc : ${JSON.stringify(f)}`);
      await page.click('section[data-vue="plan"] .fiche-meuble button:text-is("Fermer")');
      f = await fiche();
      verifier(f.hash === "#plan" && f.ici === 0 && f.corps.includes("Touchez un meuble"), `${t}, Fermer : ${JSON.stringify(f)}`);
      await page.focus(BANC);
      await page.keyboard.press("Enter");
      f = await fiche();
      verifier(ouverte(f), `${t}, Entrée sur le banc : ${JSON.stringify(f)}`);
    }

    // en comparaison, toucher le banc n'ouvre rien
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plan");
    const b = await page.evaluate(s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }, BANC);
    await ouvrir(page, DOC + "#plan?c=victor");
    await comparee(page, "plan", "plan en comparaison : pas d'étiquettes");
    await page.mouse.click(b[0], b[1]);
    let f = await fiche();
    verifier(f.hash === "#plan?c=victor" && f.ici === 0 && f.corps.includes("Touchez un meuble"),
             `plan en comparaison, toucher le banc : ${JSON.stringify(f)}`);
  });

  // ------------------------------------------------------------------ « Position » : le repère affiché, sur le mini-plan
  await partie("position", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    // marques du mini-plan de la vue (traits de coupe, points de vue) : celles qui portent ici, et leur opacité calculée
    const position = vue => page.evaluate(v => {
      const marques = [...document.querySelectorAll(`section[data-vue="${v}"] .mini [data-k]`)];
      const opacite = x => +getComputedStyle(x)[x.matches("line") ? "strokeOpacity" : "opacity"];
      return {ici: marques.filter(x => x.classList.contains("ici")).map(x => x.dataset.k), tous: marques.map(x => x.dataset.k),
              opacite: Object.fromEntries(marques.map(x => [x.dataset.k, opacite(x)]))};
    }, vue);
    const marquee = ([v, k]) => {
      const x = document.querySelector(`section[data-vue="${v}"] .mini [data-k="${k}"]`);
      return Boolean(x && x.classList.contains("ici"));
    };
    for (const [variante, adresse] of Object.entries(VARIANTES)) {
      for (const [vue, k, autre] of [["coupes", "B", "C"], ["iso", "se", "no"], ["camera", "couloir", "banc"]]) {
        const t = `${variante}, Position de ${vue}`;
        await ouvrir(page, `${adresse}#${vue}?k=${k}`);
        await attendre(page, marquee, [vue, k], `${t} : ${k} n'est pas marqué`);
        let p = await position(vue);
        verifier(egal(p.ici, [k]) && p.opacite[k] === 1 && p.tous.every(x => x === k || p.opacite[x] < 0.5),
                 `${t}, ${k} : ${JSON.stringify(p)}`);
        if (vue === "iso") verifier(!p.tous.includes("ne"), `${t} : un cône pour NE, coin sans rendu ${JSON.stringify(p.tous)}`);
        await page.evaluate(([v, k]) => { location.hash = `#${v}?k=${k}`; }, [vue, autre]);
        await attendre(page, marquee, [vue, autre], `${t} : ${autre} n'est pas marqué après le changement de repère`);
        p = await position(vue);
        verifier(egal(p.ici, [autre]), `${t}, puis ${autre} : ${JSON.stringify(p)}`);
      }
    }
  });

  // ------------------------------------------------------------------ comparaison
  await partie("comparaison", async () => {
    await ouvrir(page, VARIANTES.victor + "#coupes?k=D&c=principale");
    await comparee(page, "coupes", "coupe D : pas d'étiquettes");
    let et = await etiquettes(page, "coupes");
    verifier(egal(et, ["Victor", "Principale : pas d'équivalent"]), `coupe D comparée à la principale : ${JSON.stringify(et)}`);

    for (const [vue, k] of [["iso", "so"], ["camera", "banc"]]) {
      await ouvrir(page, `${DOC}#${vue}?k=${k}&c=victor`);
      await comparee(page, vue, `${vue} ${k} comparé : pas d'étiquettes`);
      et = await etiquettes(page, vue);
      const rendus = await page.evaluate(v => [...document.querySelectorAll(`section[data-vue="${v}"] .scene > .element img:not(.calque)`)]
        .filter(i => i.checkVisibility()).map(i => i.getAttribute("src")), vue);
      verifier(egal(et, ["Principale", "Victor"]) && egal(rendus, [`rendus/principale-${vue === "iso" ? "iso_" : ""}${k}.jpg`,
                                                                  `rendus/victor-${vue === "iso" ? "iso_" : ""}${k}.jpg`]),
               `${vue} ${k} comparé à Victor : étiquettes ${JSON.stringify(et)}, rendus ${JSON.stringify(rendus)}`);
      await imagesChargees(page, vue);
    }
  });

  // ------------------------------------------------------------------ teinte « Moka »
  await partie("teinte", async () => {
    const MOKA = "#d6bba6";
    const pentes = hex => [1, 3, 5].map(i => parseInt(hex.substr(i, 2), 16) / 255 / 0.8);
    const proches = (a, b) => a.length === b.length && a.every((x, i) => Math.abs(x - b[i]) < 0.001);
    const teinte = () => page.evaluate(() => {
      const pente = c => +document.querySelector(`#filtre-teinte feFunc${c}`).getAttribute("slope");
      const calques = [...document.querySelectorAll("section.vue img.calque")].filter(i => i.checkVisibility());
      const pastille = document.querySelector("#n-options");
      return {india: getComputedStyle(document.documentElement).getPropertyValue("--india").trim().toLowerCase(),
              dessin: getComputedStyle(document.querySelector('section[data-vue="plan"] .indiap')).fill,
              pentes: ["R", "G", "B"].map(pente), calques: calques.length,
              filtres: calques.every(i => getComputedStyle(i).filter.includes("filtre-teinte")),
              pastille: pastille.hidden ? "" : pastille.textContent};
    });
    await ouvrir(page, DOC + "#iso?k=so");
    await page.evaluate(() => localStorage.clear());
    await ouvrir(page, DOC + "#iso?k=so");
    await page.click("#c-options");
    await attendre(page, () => document.querySelector("#panneau-options").checkVisibility(), null, "teinte : le panneau ne s'ouvre pas");
    await page.click('#panneau-options [data-v="color_moka"]');
    let tm = await teinte();
    verifier(tm.india === MOKA && tm.dessin === "rgb(214, 187, 166)", `Moka : --india ${tm.india}, dessin ${tm.dessin}`);
    verifier(proches(tm.pentes, pentes(MOKA)) && tm.calques === 1 && tm.filtres, `Moka : filtre des rendus ${JSON.stringify(tm)}`);
    await page.keyboard.press("Escape");
    await ouvrir(page, VARIANTES.victor + "#iso?k=so");
    tm = await teinte();
    verifier(tm.india === MOKA && proches(tm.pentes, pentes(MOKA)) && tm.pastille === "1",
             `Moka retrouvé sur Victor : ${JSON.stringify(tm)}`);

    // le panneau et ses 52 teintes tiennent dans l'écran ; il défile sous son titre et sa croix, la teinte choisie
    // reste lisible en bas, et aucune teinte (au clavier ou en fin de liste) ne reste cachée sous l'un ou l'autre
    for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
      const t = `${largeur} px, panneau`;
      await page.setViewportSize({width: largeur, height: hauteur});
      await ouvrir(page, DOC + "#plan");
      await page.click("#c-options");
      await attendre(page, () => document.querySelector("#panneau-options").checkVisibility(), null, `${t} : il ne s'ouvre pas`);
      const d = await debordements(page);
      verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
      const p = await page.evaluate(() => {
        const f = document.querySelector("#panneau-options"), r = f.getBoundingClientRect();
        const boutons = [...f.querySelectorAll("[data-v]")], dernier = boutons[boutons.length - 1];
        const boite = e => e.getBoundingClientRect();
        const dans = e => { const b = boite(e); return b.top >= r.top - 1 && b.bottom <= r.bottom + 1; };
        // un bouton est lisible s'il est dans le panneau, ni sous le titre ni sous la ligne de la teinte choisie
        const libre = e => dans(e) && boite(e).top >= boite(f.querySelector("h2")).bottom - 1
          && (boite(e).bottom <= boite(f.querySelector(".info")).top + 1 || boite(e).top >= boite(f.querySelector(".info")).bottom - 1);
        const etat = () => ({fermer: dans(f.querySelector(".fermer")), info: dans(f.querySelector(".info"))});
        const res = {n: boutons.length, haut: r.top, bas: r.bottom, h: innerHeight, defile: f.scrollHeight > f.clientHeight,
                     info: f.querySelector(".info").textContent, coupes: boutons.filter(x => x.scrollWidth > x.clientWidth + 1).map(x => x.textContent)};
        res.enHaut = etat();
        f.scrollTop = (f.scrollHeight - f.clientHeight) / 2;
        res.auMilieu = etat();
        f.scrollTop = f.scrollHeight;
        res.aLaFin = {...etat(), dernier: libre(dernier)};
        f.scrollTop = 0;
        res.clavier = boutons.filter(b => { b.focus(); return !libre(b); }).map(b => b.textContent);
        return res;
      });
      verifier(p.n === 52 && p.haut >= 0 && p.bas <= p.h + 1 && p.defile, `${t} : ${JSON.stringify(p)}`);
      verifier(p.info.startsWith("Moka"), `${t} : teinte choisie « ${p.info} »`);
      verifier(p.enHaut.fermer && p.enHaut.info && p.auMilieu.fermer && p.auMilieu.info && p.aLaFin.fermer && p.aLaFin.info,
               `${t} : la croix ou la teinte choisie sort du panneau en le faisant défiler ${JSON.stringify([p.enHaut, p.auMilieu, p.aLaFin])}`);
      verifier(p.aLaFin.dernier, `${t} : la dernière teinte reste cachée en fin de liste`);
      verifier(p.clavier.length === 0, `${t} : teintes cachées une fois atteintes au clavier ${JSON.stringify(p.clavier)}`);
      verifier(p.coupes.length === 0, `${t} : noms de teintes coupés ${JSON.stringify(p.coupes)}`);
      await page.keyboard.press("Escape");
    }
    await page.evaluate(() => localStorage.clear());
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
    let r = await suivre("/entree-amenagement.html#coupe-b-b-mur-de-la-salle-de-bain", "/entree/amenagement/");
    verifier(r.hash === "#coupes?k=B" && egal(r.vues, ["coupes"]), `ancienne coupe B : ${JSON.stringify(r)}`);
    r = await suivre("/entree-amenagement-victor.html", "/entree/amenagement/victor.html");
    verifier(r.hash === "" && egal(r.vues, ["plan"]), `ancienne page de Victor : ${JSON.stringify(r)}`);
    r = await suivre("/entree-amenagement-victor.html#coupe-d-d-mur-ouest-de-l-entree", "/entree/amenagement/victor.html");
    verifier(r.hash === "#coupes?k=D", `ancienne coupe D de Victor : ${JSON.stringify(r)}`);
    r = await suivre("/entree-amenagement-victor.html#differences-avec-la-v4-3", "/entree/amenagement/victor.html");
    verifier(r.hash === "#explication" && egal(r.vues, ["explication"]), `ancienne ancre « différences avec la V4.3 » : ${JSON.stringify(r)}`);
    r = await suivre("/entree-amenagement.html#points-a-verifier", "/entree/amenagement/");
    verifier(r.hash === "#explication" && egal(r.vues, ["explication"]), `ancienne ancre « points à vérifier » : ${JSON.stringify(r)}`);
    r = await suivre("/entree-amenagement.html#changements", "/entree/amenagement/historique.html");
    verifier(r.chemin === "/entree/amenagement/historique.html" && r.hash === "", `ancienne ancre « changements » : ${JSON.stringify(r)}`);
  });

  // ------------------------------------------------------------------ historique
  await partie("historique", async () => {
    await ouvrir(page, DOC + "historique.html");
    const h = await page.evaluate(() => ({
      variantes: [...document.querySelectorAll("section.variante h2")].map(x => x.textContent),
      figees: [...document.querySelectorAll("ul.figees li")].map(li => li.textContent.trim()),
      liens: [...document.querySelectorAll("ul.figees a")].map(a => a.href),
      journaux: [...document.querySelectorAll("ol.fil")].map(o => o.children.length),
    }));
    verifier(egal(h.variantes, ["Principale", "Victor"]), `historique : variantes ${JSON.stringify(h.variantes)}`);
    verifier(egal(h.figees, ["V3.3 1 octobre 2026", "V2 1 octobre 2026", "V1 1 octobre 2026"]), `historique : versions figées ${JSON.stringify(h.figees)}`);
    verifier(h.journaux.length === 2 && h.journaux.every(n => n > 0), `historique : journaux ${JSON.stringify(h.journaux)}`);
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
        for (const [variante, adresse] of Object.entries(VARIANTES)) {
          await p.goto(adresse);
          const s = await p.evaluate(() => ({
            classe: document.documentElement.className,
            vues: [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility())
              .map(x => { const r = x.getBoundingClientRect(); return [x.dataset.vue, Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; }),
          }));
          const suite = s.vues.every((v, i) => i === 0 || v[1] >= s.vues[i - 1][2] - 1);
          verifier(s.classe.includes("sans-js") && egal(s.vues.map(v => v[0]), VUES) && suite,
                   `sans JavaScript, ${largeur} px, ${variante} : ${JSON.stringify(s)}`);
          const d = await debordements(p);
          verifier(!d.some(x => x.startsWith("page")), `sans JavaScript, ${largeur} px, ${variante} : déborde (${d.join(" ; ")})`);
        }
      }
    } finally {
      await sansJs.close();
    }
  });

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
