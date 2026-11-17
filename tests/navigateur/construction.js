/* Document de construction : l'étagère d'essai (pièce « Atelier », tests/fixtures/essai/meuble.py), trois variantes.
   Six vues : Plans (l'élévation, avec Mesurer), Iso (la vue iso, zoom seul), Découpe, Montage, Achats, Explication.
   « Actuelle » (atelier/etagere/) a ses six vues remplies et deux sections d'achats ; « Rangs » (rangs.html) n'a
   pas de Montage (onglet grisé, « Sans objet ») ; « Escalier » (escalier.html) n'a pas de vue iso (Iso vide,
   « Sans objet », onglet actif).
   À 1440, 1100 et 390 px :
   - Onglets : ordre, Plans courant, un clic montre la vue et l'écrit dans l'adresse.
   - Variante : le choix de la variante garde la vue et le repère.
   - Comparaison sur Plans (élévation face à Rangs) et sur Iso (iso face à Escalier qui n'en a pas) ; pas de
     Comparer ailleurs.
   - Onglet grisé de Rangs ; Mesurer dans Plans, absent d'Iso ; l'ancienne adresse #plans?k=iso ouvre l'onglet Iso.
   - Largeur : chaque repère attendu de Plans et d'Iso, un à un ; à 390 px, rien ne déborde dans aucune vue et la
     quantité reste en tête de chaque carte du débit ; à 1100 et 1440 px, ni la barre ni la fiche.
   - Sans JavaScript (1440 et 390 px) : les six vues l'une sous l'autre ; aucune erreur de console ni 404.
   Lancé par tests/navigateur/lancer.sh, qui ouvre la racine du site d'essai avant d'appeler ce script. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/atelier/etagere/`;
  const VARIANTES = {actuelle: DOC, rangs: DOC + "rangs.html", escalier: DOC + "escalier.html"};
  const VUES = ["plans", "iso", "decoupe", "montage", "achats", "explication"];
  const NOMS = ["Plans", "Iso", "Découpe", "Montage", "Achats", "Explication"];
  const LARGEURS = [[1440, 900], [1100, 800], [390, 844]];
  // repères attendus par variante et par vue (segments, ou l'élément d'un dessin seul) ; les autres vues n'en ont pas
  const REPERES = {actuelle: {plans: ["elevation"], iso: ["iso"]}, rangs: {plans: ["elevation"], iso: ["iso"]},
                   escalier: {plans: ["elevation"], iso: []}};
  const echecs = [], erreurs = [];
  let lieu = "";   // la partie en cours, pour situer une erreur de console
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };
  const egal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  const preparer = async p => {
    p.on("console", m => { if (m.type() === "error") erreurs.push(`${lieu}, console : ${m.text()}`); });
    p.on("pageerror", e => erreurs.push(`${lieu}, page : ${e.message}`));
    p.on("response", r => { if (r.status() >= 400) erreurs.push(`${lieu}, ${r.status()} : ${r.url()}`); });
    p.on("requestfailed", r => {   // une requête interrompue par le changement de page n'est pas une erreur du site
      const raison = (r.failure() || {}).errorText || "";
      if (!raison.includes("ERR_ABORTED")) erreurs.push(`${lieu}, échec : ${r.url()} (${raison})`);
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

  // Ce qui dépasse : la page en largeur ; la barre, les onglets, la scène, la fiche et le panneau hors de l'écran ;
  // un contenu plus large que sa boîte (barre, fiche, article de lecture), donc coupé ou à faire défiler en largeur.
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

  // Ce que debordements ne voit pas : un contenu plus large que son cadre défilant (overflow-x auto, scroll ou hidden),
  // dans la vue visible, hors de la scène. Rien n'a le droit de défiler en largeur à 390 px : le débit (.debit) et les
  // achats (.defile) y tiennent, rangés en cartes.
  const debordementsCaches = p => p.evaluate(() => {
    const section = [...document.querySelectorAll("#contenu > section.vue")].find(s => s.checkVisibility());
    if (!section) return ["aucune vue visible"];
    return [...section.querySelectorAll("*")]
      .filter(e => !e.closest(".scene") && e.checkVisibility()
                   && ["auto", "scroll", "hidden"].includes(getComputedStyle(e).overflowX)
                   && e.scrollWidth > e.clientWidth + 1)
      .map(e => `${e.tagName.toLowerCase()}.${[...e.classList].join(".")} : contenu de ${e.scrollWidth} px dans ${e.clientWidth}`);
  });

  // Cartes du débit (390 px) : dans chaque carte, la quantité (td.d) est sur la rangée du repère (même haut, à deux
  // pixels près) et à sa droite, au bout de la carte, quel que soit le rang de sa colonne.
  const quantitesEnTete = p => p.evaluate(() => {
    const res = [], lignes = [...document.querySelectorAll('section[data-vue="decoupe"] table.cartes tbody tr')];
    if (!lignes.length) return ["aucune carte de débit"];
    for (const [i, tr] of lignes.entries()) {
      const rep = tr.querySelector("td:first-child"), qte = tr.querySelector("td.d");
      if (!qte) { res.push(`carte ${i + 1} : pas de quantité`); continue; }
      const a = rep.getBoundingClientRect(), b = qte.getBoundingClientRect(), t = tr.getBoundingClientRect();
      if (Math.abs(a.top - b.top) > 2 || b.left < a.right || t.right - b.right > 2)
        res.push(`carte ${i + 1} : repère ${Math.round(a.left)},${Math.round(a.top)}, quantité ${Math.round(b.left)},`
                 + `${Math.round(b.top)} (bout de carte ${Math.round(t.right)}, quantité finit à ${Math.round(b.right)})`);
    }
    return res;
  });

  // chaque partie est vérifiée même si une autre a levé une exception
  const partie = async (nom, f) => {
    lieu = nom;
    try { await f(); } catch (e) { echecs.push(`${nom} : exception : ${e.message.split("\n")[0]}`); }
  };

  // ce que montre la page : adresse, vues visibles, onglet courant, Comparer, « avec », étiquettes et clones
  const etat = p => p.evaluate(() => {
    const vu = e => Boolean(e && e.checkVisibility());
    const avec = document.querySelector("#c-autre");
    return {
      url: location.href,
      vues: [...document.querySelectorAll("#contenu > section.vue")].filter(vu).map(s => s.dataset.vue),
      courant: [...document.querySelectorAll("nav.vues a[aria-current='page']")].map(a => a.dataset.vue),
      comparer: vu(document.querySelector("#c-comp")),
      avec: vu(avec && avec.closest("label")),
      etiquettes: [...document.querySelectorAll(".bandeau .etiq-var")].filter(vu).map(e => e.textContent),
      toutesEtiquettes: document.querySelectorAll(".etiq-var").length,
      clones: document.querySelectorAll(".scene > .element.b").length,
      poignees: [...document.querySelectorAll(".poignee")].filter(vu).length,
    };
  });
  const vueVisible = (p, vue, message) => attendre(p, v => {
    const s = [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility());
    return s.length === 1 && s[0].dataset.vue === v;
  }, vue, message);

  await sansPolices(page.context());
  await preparer(page);

  for (const [largeur, hauteur] of LARGEURS) {
    await page.setViewportSize({width: largeur, height: hauteur});
    const L = `${largeur} px`;

    // ---------------------------------------------------------------- 1. onglets
    await partie(`1 onglets, ${L}`, async () => {
      await ouvrir(page, DOC);
      const o = await page.evaluate(() => ({
        ordre: [...document.querySelectorAll("nav.vues a[data-vue]")].map(a => [a.dataset.vue, a.textContent.trim()]),
        vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
        courant: [...document.querySelectorAll("nav.vues a[aria-current='page']")].map(a => a.dataset.vue),
      }));
      verifier(egal(o.ordre, VUES.map((v, i) => [v, NOMS[i]])), `1 onglets, ${L} : ordre ${JSON.stringify(o.ordre)}`);
      verifier(egal(o.vues, ["plans"]) && egal(o.courant, ["plans"]), `1 onglets, ${L} : à l'ouverture ${JSON.stringify(o)}`);
      for (const vue of [...VUES.slice(1), VUES[0]]) {
        await page.click(`nav.vues a[data-vue="${vue}"]`);
        await vueVisible(page, vue, `1 onglets, ${L} : clic sur ${vue}, la section ne s'affiche pas`);
        const e = await etat(page);
        verifier(new URL(e.url).hash === `#${vue}` && egal(e.vues, [vue]) && egal(e.courant, [vue]),
                 `1 onglets, ${L} : clic sur ${vue} : ${JSON.stringify([e.url, e.vues, e.courant])}`);
      }
    });

    // ---------------------------------------------------------------- 2. variante
    await partie(`2 variante, ${L}`, async () => {
      for (const [depart, choix, arrivee, vue] of [[DOC + "#decoupe", "rangs", DOC + "rangs.html#decoupe", "decoupe"],
                                                   [DOC + "rangs.html#iso?k=iso", "actuelle", DOC + "#iso?k=iso", "iso"],
                                                   [DOC + "rangs.html#plans?k=elevation", "actuelle", DOC + "#plans?k=elevation", "plans"]]) {
        const t = `2 variante, ${L}, de ${depart.slice(DOC.length) || "./"} vers ${choix}`;
        await ouvrir(page, depart);
        await page.selectOption("#c-variante", choix);
        try { await page.waitForURL(arrivee); } catch (x) { echecs.push(`${t} : adresse ${page.url()}, attendu ${arrivee}`); continue; }
        await vueVisible(page, vue, `${t} : la section ${vue} ne s'affiche pas`);
        const e = await page.evaluate(() => ({
          variante: document.body.dataset.variante, choix: document.querySelector("#c-variante").value,
          elements: [...document.querySelectorAll('section[data-vue="plans"] .scene > .element, section[data-vue="iso"] .scene > .element')]
            .filter(x => x.checkVisibility()).map(x => x.dataset.k),
        }));
        const attendu = {decoupe: [], iso: ["iso"], plans: ["elevation"]}[vue];
        verifier(e.variante === choix && e.choix === choix && egal(e.elements, attendu),
                 `${t} : ${JSON.stringify(e)}`);
      }
    });

    // ---------------------------------------------------------------- 3. comparaison
    await partie(`3 comparaison, ${L}`, async () => {
      let t = `3 comparaison, ${L}, élévation avec Rangs`;
      await ouvrir(page, DOC + "#plans?k=elevation&c=rangs");
      await attendre(page, () => document.querySelectorAll('section[data-vue="plans"] .bandeau .etiq-var').length === 2,
                     null, `${t} : pas d'étiquettes`);
      let e = await etat(page);
      verifier(egal(e.etiquettes, ["Actuelle", "Rangs"]) && e.clones === 1 && e.poignees === 1 && e.comparer && e.avec,
               `${t} : ${JSON.stringify(e)}`);
      t = `3 comparaison, ${L}, iso avec Escalier`;
      await ouvrir(page, DOC + "#iso?k=iso&c=escalier");
      await attendre(page, () => document.querySelectorAll('section[data-vue="iso"] .bandeau .etiq-var').length === 2,
                     null, `${t} : pas d'étiquettes`);
      e = await etat(page);
      const choixAvec = await page.evaluate(() => [...document.querySelectorAll("#c-autre option")].map(o => o.value));
      verifier(egal(e.etiquettes, ["Actuelle", "Escalier : pas d'équivalent"]) && e.clones === 0 && e.poignees === 0
               && e.comparer && e.avec && egal(choixAvec, ["rangs", "escalier"]),
               `${t} : ${JSON.stringify(e)}, « avec » propose ${JSON.stringify(choixAvec)}`);
    });

    // ---------------------------------------------------------------- 4. pas de Comparer hors de Plans et d'Iso
    await partie(`4 pas de Comparer, ${L}`, async () => {
      for (const vue of VUES.slice(2)) {
        for (const suite of ["", "?c=rangs"]) {
          const t = `4 pas de Comparer, ${L}, #${vue}${suite}`;
          await ouvrir(page, `${DOC}#${vue}${suite}`);
          await vueVisible(page, vue, `${t} : la section ne s'affiche pas`);
          await page.waitForLoadState("networkidle");   // étiquettes et clones viendraient après les chargements
          const e = await etat(page);
          verifier(!e.comparer && !e.avec && e.toutesEtiquettes === 0 && e.clones === 0, `${t} : ${JSON.stringify(e)}`);
        }
      }
    });

    // ---------------------------------------------------------------- 5. onglet grisé
    await partie(`5 onglet grisé, ${L}`, async () => {
      const t = `5 onglet grisé, ${L}`;
      await ouvrir(page, VARIANTES.rangs + "#plans");
      const a = await page.evaluate(() => {
        const x = document.querySelector('nav.vues a[data-vue="montage"]');
        return {grise: x.getAttribute("aria-disabled"), titre: x.getAttribute("title"),
                autres: [...document.querySelectorAll('nav.vues a[aria-disabled="true"]')].map(y => y.dataset.vue)};
      });
      verifier(a.grise === "true" && a.titre === "Sans objet" && egal(a.autres, ["montage"]), `${t} : onglet ${JSON.stringify(a)}`);
      // Playwright attend qu'un lien aria-disabled devienne actif : force clique quand même, à la souris
      await page.click('nav.vues a[data-vue="montage"]', {force: true});
      const e = await etat(page);
      verifier(new URL(e.url).hash === "#plans" && egal(e.vues, ["plans"]) && egal(e.courant, ["plans"]),
               `${t} : un clic change la vue ${JSON.stringify([e.url, e.vues, e.courant])}`);
      await ouvrir(page, VARIANTES.rangs + "#montage");
      await vueVisible(page, "montage", `${t} : rangs.html#montage ne montre pas Montage`);
      const vide = await page.evaluate(() => {
        const v = document.querySelector('section[data-vue="montage"] .vide');
        return v && v.checkVisibility() ? v.textContent : null;
      });
      verifier(vide === "Sans objet", `${t} : rangs.html#montage montre « ${vide} »`);
    });

    // ---------------------------------------------------------------- 6. Mesurer, ancienne adresse de l'iso
    await partie(`6 Mesurer, ${L}`, async () => {
      const t = `6 Mesurer, ${L}`;
      const mesure = () => page.evaluate(() => {
        const s = document.querySelector('section[data-vue="plans"]'), b = s.querySelector(".b-mesure");
        const iso = document.querySelector('section[data-vue="iso"]');
        return {visible: Boolean(b && b.checkVisibility()), presse: b && b.getAttribute("aria-pressed"),
                scene: s.querySelector(".scene").classList.contains("mesure"),
                element: [...s.querySelectorAll(".scene > .element")].filter(x => x.checkVisibility()).map(x => x.dataset.k),
                iso: {outils: iso.dataset.outils, bouton: iso.querySelectorAll(".b-mesure").length}};
      });
      await ouvrir(page, DOC + "#plans?k=elevation");
      let m = await mesure();
      verifier(m.visible && m.presse === "false" && egal(m.element, ["elevation"]), `${t} : sur l'élévation ${JSON.stringify(m)}`);
      verifier(m.iso.bouton === 0 && !/mesure/.test(m.iso.outils || ""), `${t} : Mesurer présent dans Iso ${JSON.stringify(m.iso)}`);
      await page.click('section[data-vue="plans"] .b-mesure');
      m = await mesure();
      verifier(m.presse === "true" && m.scene, `${t} : Mesurer ne s'enfonce pas ${JSON.stringify(m)}`);
      // ancienne adresse (l'iso était un repère de Plans) : l'onglet Iso s'ouvre, l'adresse est corrigée
      await ouvrir(page, DOC + "#plans?k=iso");
      await vueVisible(page, "iso", `${t} : #plans?k=iso n'ouvre pas Iso`);
      await attendre(page, () => location.hash === "#iso?k=iso", null, `${t} : #plans?k=iso devient ${page.url()}, attendu #iso?k=iso`);
      const iso = await page.evaluate(() => ({
        courant: [...document.querySelectorAll("nav.vues a[aria-current='page']")].map(a => a.dataset.vue),
        element: [...document.querySelectorAll('section[data-vue="iso"] .scene > .element')].filter(x => x.checkVisibility()).map(x => x.dataset.k),
        mesure: [...document.querySelectorAll(".b-mesure")].filter(x => x.checkVisibility()).length,
      }));
      verifier(egal(iso, {courant: ["iso"], element: ["iso"], mesure: 0}), `${t} : #plans?k=iso montre ${JSON.stringify(iso)}`);
    });

    // ---------------------------------------------------------------- 7. largeur
    await partie(`7 largeur, ${L}`, async () => {
      for (const [variante, adresse] of Object.entries(VARIANTES)) {
        for (const vue of VUES) {
          await ouvrir(page, `${adresse}#${vue}`);
          await vueVisible(page, vue, `7 largeur, ${L}, ${variante}, ${vue} : la section ne s'affiche pas`);
          // repères des segments ; un seul dessin n'a pas de segments : celui de son élément
          const ks = await page.evaluate(v => {
            const s = `section[data-vue="${v}"]`;
            const segments = [...document.querySelectorAll(`${s} .segments button[data-k]:not(:disabled)`)];
            const elements = [...document.querySelectorAll(`${s} .scene > .element:not(.b)`)];
            return (segments.length ? segments : elements).map(b => b.dataset.k).filter(k => k);
          }, vue);
          const attendus = REPERES[variante][vue] || [];
          verifier(egal(ks, attendus), `7 largeur, ${L}, ${variante}, ${vue} : repères ${JSON.stringify(ks)}, `
                   + `attendu ${JSON.stringify(attendus)}`);
          for (const k of ks.length ? ks : [""]) {
            const t = `7 largeur, ${L}, ${variante}, ${vue}${k ? " " + k : ""}`;
            if (k) {
              await page.evaluate(([v, k]) => { location.hash = `#${v}?k=${k}`; }, [vue, k]);
              await attendre(page, ([v, k]) => {
                const e = document.querySelector(`section[data-vue="${v}"] .scene > .element[data-k="${k}"]`);
                return e && e.checkVisibility();
              }, [vue, k], `${t} : l'élément ne s'affiche pas`);
            }
            const d = await debordements(page);
            if (largeur === 390) {
              verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
              const caches = await debordementsCaches(page);
              verifier(caches.length === 0, `${t} : déborde dans un cadre défilant (${caches.join(" ; ")})`);
              if (vue === "decoupe") {
                const q = await quantitesEnTete(page);
                verifier(q.length === 0, `${t} : quantité hors de la première rangée (${q.join(" ; ")})`);
              }
            }
            else {
              const fiche = await page.evaluate(v => {
                const f = document.querySelector(`section[data-vue="${v}"] .fiche`);
                return Boolean(f && f.checkVisibility());
              }, vue);
              verifier(!attendus.length || fiche, `${t} : la fiche n'est pas visible`);
              const barreFiche = d.filter(x => /^(barre|onglets|\.fiche) /.test(x));
              verifier(barreFiche.length === 0, `${t} : la barre ou la fiche déborde (${barreFiche.join(" ; ")})`);
            }
          }
        }
      }
    });
  }

  // ---------------------------------------------------------------- 8. sans JavaScript
  await partie("8 sans JavaScript", async () => {
    const sansJs = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      await sansPolices(sansJs);
      const p = await sansJs.newPage();
      await preparer(p);
      for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
        await p.setViewportSize({width: largeur, height: hauteur});
        for (const [variante, adresse] of Object.entries(VARIANTES)) {
          const t = `8 sans JavaScript, ${largeur} px, ${variante}`;
          lieu = t;
          await p.goto(adresse);
          const s = await p.evaluate(() => ({
            classe: document.documentElement.className,
            vues: [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility())
              .map(x => { const r = x.getBoundingClientRect(); return [x.dataset.vue, Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; }),
            texte: document.body.innerText,
          }));
          const suite = s.vues.every((v, i) => i === 0 || v[1] >= s.vues[i - 1][2] - 1);
          verifier(s.classe.includes("sans-js") && egal(s.vues.map(v => v[0]), VUES) && suite,
                   `${t} : ${JSON.stringify({classe: s.classe, vues: s.vues})}`);
          verifier(s.texte.includes("Liste de débit"), `${t} : « Liste de débit » absent`);
          if (variante === "actuelle") verifier(s.texte.includes("Sous-total"), `${t} : « Sous-total » absent`);
          const d = await debordements(p);
          verifier(!d.some(x => x.startsWith("page")), `${t} : déborde (${d.join(" ; ")})`);
        }
      }
    } finally {
      await sansJs.close();
    }
  });

  // ---------------------------------------------------------------- 9. console : les erreurs sont rendues dans `erreurs`
  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
