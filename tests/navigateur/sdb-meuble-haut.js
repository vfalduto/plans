/* @site reel : le meuble haut de la salle de bain sur le vrai site/, construit par python3 site.py (lancer.sh le sert).
   - Vues : les cinq vues et les quatre repères de Plans, à 1440, 1100 et 390 px : sans erreur de console ni réponse en
     erreur, rien ne déborde (tableaux, fiches de perçage, calepinages).
   - Entrée sans fragment : Plans, vue iso ; ni Comparer, ni variante, ni Personnaliser.
   - Mesurer : les deux bouts de la plus longue cote de la pose de face donnent « Mesuré : 204 cm » ; caché sur l'iso.
   - Fiche de Plans : les liens Découpe et Montage ; Montage : les boutons vers la pose de face et en coupe.
   - Montage : trois étapes numérotées de 1 à 3 et aucun <li> imbriqué (il prendrait une pastille numérotée).
   - Dessins : aucun aplat noir, aucun texte hors du viewBox (Plans), aucun aplat noir dans Découpe et Montage.
   - Achats : totaux, lien « Meuble bas » vers les achats du meuble bas.
   - Anciennes adresses (sdb-meuble-haut.html, sdb-meuble-achats.html), historique (deux entrées, huit versions figées)
     et la page sans JavaScript. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/sdb/meuble-haut/`;
  const VUES = ["plans", "decoupe", "montage", "achats", "explication"];
  const REPERES = ["iso", "eclate", "elevation", "coupe"];
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
  const partie = async (nom, f) => {
    try { await f(); } catch (e) { echecs.push(`${nom} : exception : ${e.message.split("\n")[0]}`); }
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
  // le repère k de Plans est affiché
  const repereAffiche = (p, k, t) => attendre(p, k => {
    const e = document.querySelector(`section[data-vue="plans"] .scene > .element[data-k="${k}"]`);
    return e && e.checkVisibility();
  }, k, `${t} : le repère ne s'affiche pas`);
  const vueAffichee = (p, vue, t) => attendre(p, v => {
    const s = document.querySelector(`section[data-vue="${v}"]`);
    return s && s.checkVisibility();
  }, vue, `${t} : la vue ne s'affiche pas`);

  await sansPolices(page.context());
  await preparer(page);

  // repères de dessin dont un texte sort du viewBox : "repère" → raison (vide : aucun)
  const GARDES = {};

  // ------------------------------------------------------------------ 1. toutes les vues, tous les repères, toutes les largeurs
  await partie("vues", async () => {
    for (const [largeur, hauteur] of LARGEURS) {
      await page.setViewportSize({width: largeur, height: hauteur});
      for (const vue of VUES) {
        const ks = vue === "plans" ? REPERES : [""];
        for (const k of ks) {
          const t = `${largeur} px, ${vue}${k ? " " + k : ""}`;
          await ouvrir(page, `${DOC}#${vue}${k ? "?k=" + k : ""}`);
          await vueAffichee(page, vue, t);
          if (k) await repereAffiche(page, k, t);
          const e = await page.evaluate(() => ({
            vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
            hash: location.hash}));
          verifier(egal(e.vues, [vue]), `${t} : vues visibles ${JSON.stringify(e)}`);
          const d = await debordements(page);
          verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
        }
      }
    }
  });

  // ------------------------------------------------------------------ 2. sans fragment : Plans, iso
  await partie("sans fragment", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC);
    await repereAffiche(page, "iso", "sans fragment");
    const e = await page.evaluate(() => ({
      vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
      elements: [...document.querySelectorAll('section[data-vue="plans"] .scene > .element')].filter(x => x.checkVisibility()).map(x => x.dataset.k),
      comp: !!document.querySelector("#c-comp"), variante: !!document.querySelector("#c-variante"),
      perso: document.body.innerText.includes("Personnaliser")}));
    verifier(egal(e.vues, ["plans"]) && egal(e.elements, ["iso"]), `sans fragment : ${JSON.stringify(e)}`);
    verifier(!e.comp && !e.variante && !e.perso, `sans fragment : Comparer, variante ou Personnaliser présent ${JSON.stringify(e)}`);
  });

  // ------------------------------------------------------------------ 3. Mesurer
  await partie("Mesurer", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plans?k=elevation");
    await repereAffiche(page, "elevation", "Mesurer");
    await page.click('section[data-vue="plans"] .b-mesure');
    const bouts = await page.evaluate(() => {
      const svg = document.querySelector('section[data-vue="plans"] .scene > .element[data-k="elevation"] > svg');
      const lignes = [...svg.querySelectorAll("line.dim")];
      const long = lignes.reduce((a, b) => Math.hypot(b.x2.baseVal.value - b.x1.baseVal.value, b.y2.baseVal.value - b.y1.baseVal.value)
        > Math.hypot(a.x2.baseVal.value - a.x1.baseVal.value, a.y2.baseVal.value - a.y1.baseVal.value) ? b : a);
      const m = long.getScreenCTM();
      const pt = (x, y) => { const p = svg.createSVGPoint(); p.x = x; p.y = y; const q = p.matrixTransform(m); return [q.x, q.y]; };
      return {a: pt(long.x1.baseVal.value, long.y1.baseVal.value), b: pt(long.x2.baseVal.value, long.y2.baseVal.value),
              l: innerWidth, h: innerHeight};
    });
    for (const [x, y] of [bouts.a, bouts.b]) await page.mouse.click(x, y);
    const texte = await page.evaluate(() => {
      const m = document.querySelector('section[data-vue="plans"] .bandeau .mes');
      return m && !m.hidden ? m.textContent.trim() : "";
    });
    verifier(texte === "Mesuré : 204 cm", `Mesurer : bandeau « ${texte} » (bouts ${JSON.stringify(bouts)})`);
    for (const k of ["iso", "eclate"]) {
      await ouvrir(page, DOC + `#plans?k=${k}`);
      await repereAffiche(page, k, `Mesurer, ${k}`);
      const visible = await page.evaluate(() => document.querySelector('section[data-vue="plans"] .b-mesure').checkVisibility());
      verifier(!visible, `Mesurer : le bouton reste visible sur ${k}`);
    }
  });

  // ------------------------------------------------------------------ 4. liens : fiche de Plans, boutons du Montage
  await partie("liens", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    for (const [nom, hash] of [["Découpe", "#decoupe"], ["Montage", "#montage"]]) {
      await ouvrir(page, DOC + "#plans?k=elevation");
      await repereAffiche(page, "elevation", `fiche ${nom}`);
      await page.locator(`section[data-vue="plans"] .fiche a:has-text("${nom}")`).first().click();
      await attendre(page, h => location.hash === h, hash, `fiche : le lien « ${nom} » ne mène pas à ${hash}`);
    }
    for (const [nom, k] of [["Pose, de face", "elevation"], ["Pose, en coupe", "coupe"]]) {
      await ouvrir(page, DOC + "#montage");
      await vueAffichee(page, "montage", `bouton ${nom}`);
      await page.locator(`section[data-vue="montage"] a.btn:has-text("${nom}")`).first().click();
      await attendre(page, h => location.hash === h, `#plans?k=${k}`, `montage : le bouton « ${nom} » ne mène pas à #plans?k=${k}`);
      await repereAffiche(page, k, `bouton ${nom}`);
    }
    await ouvrir(page, DOC + "#decoupe");
    await page.locator('section[data-vue="decoupe"] a:has-text("Plans")').first().click();
    await attendre(page, h => location.hash === h, "#plans?k=eclate", "découpe : le lien vers la vue éclatée ne mène pas à #plans?k=eclate");
  });

  // ------------------------------------------------------------------ 5. Montage : trois étapes, aucun <li> imbriqué
  await partie("montage", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#montage");
    await vueAffichee(page, "montage", "montage");
    const e = await page.evaluate(() => {
      const ol = document.querySelector('section[data-vue="montage"] ol.etapes');
      return {n: ol.children.length, li: ol.querySelectorAll("li").length, debut: ol.getAttribute("start"),
              ops: ol.querySelectorAll(".op").length, perc: ol.querySelectorAll("details.perc").length,
              figures: ol.querySelectorAll("figure.etape-figure svg").length};
    });
    verifier(e.n === 3 && e.li === 3 && e.debut === null, `montage : étapes ${JSON.stringify(e)}`);
    verifier(e.ops === 10 && e.perc === 2 && e.figures === 3, `montage : opérations, perçages ou schémas ${JSON.stringify(e)}`);
  });

  // ------------------------------------------------------------------ 6. dessins : pas de noir, texte dans le viewBox
  // Le svg de tête de chaque élément de Plans. site.js agrandit le viewBox des dessins de scène : le texte se compare
  // au viewBox d'origine, lu dans le HTML servi (même rang parmi les dessins de la section).
  await partie("dessins", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC);
    const html = await page.evaluate(async u => (await fetch(u)).text(), DOC);
    for (const k of REPERES) {
      const t = `dessins, ${k}`;
      await ouvrir(page, `${DOC}#plans?k=${k}`);
      await repereAffiche(page, k, t);
      const r = await page.evaluate(([v, source]) => {
        const SEL = ".scene > .element > svg";
        const section = document.querySelector(`section[data-vue="${v}"]`);
        const d0 = new DOMParser().parseFromString(source, "text/html").querySelector(`section[data-vue="${v}"]`);
        const tous = [...section.querySelectorAll(SEL)], origine = [...d0.querySelectorAll(SEL)];
        const noirs = [], dehors = [], svgs = tous.filter(s => s.checkVisibility());
        for (const svg of svgs) {
          const o = origine[tous.indexOf(svg)].getAttribute("viewBox").trim().split(/[\s,]+/).map(Number);
          const [x0, y0, w, h] = o;
          for (const e of svg.querySelectorAll("path,rect,circle,ellipse,polygon,polyline,line,text,tspan")) {
            if (e.closest("defs,clipPath,marker,mask,symbol")) continue;
            const s = getComputedStyle(e);
            if (s.fill === "rgb(0, 0, 0)" && e.tagName !== "line") noirs.push(`${e.tagName}${e.getAttribute("class") ? "." + e.getAttribute("class") : ""}`);
          }
          const versSvg = svg.getScreenCTM().inverse();
          for (const tx of svg.querySelectorAll("text")) {
            if (!tx.checkVisibility() || !tx.textContent.trim() || tx.closest(".trace-mesure")) continue;
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
      }, ["plans", html]);
      verifier(r.n > 0, `${t} : aucun dessin visible`);
      verifier(r.noirs.length === 0, `${t} : aplat noir ${JSON.stringify(r.noirs.slice(0, 8))}`);
      verifier(r.dehors.length === 0 || k in GARDES, `${t} : texte hors du viewBox ${JSON.stringify(r.dehors.slice(0, 8))}`);
    }
    // Découpe et Montage : les dessins de lecture (faces, calepinage, cartes, schémas, perçage type), sans aplat noir
    for (const vue of ["decoupe", "montage"]) {
      await ouvrir(page, `${DOC}#${vue}`);
      await vueAffichee(page, vue, `dessins de ${vue}`);
      const r = await page.evaluate(v => {
        const noirs = [], dehors = [];
        const svgs = [...document.querySelectorAll(`section[data-vue="${v}"] svg`)].filter(s => !s.classList.contains("ico"));
        for (const svg of svgs) {
          for (const e of svg.querySelectorAll("path,rect,circle,ellipse,polygon,polyline,text")) {
            if (e.closest("defs,clipPath,marker,mask,symbol")) continue;
            if (getComputedStyle(e).fill === "rgb(0, 0, 0)") noirs.push(`${e.tagName}${e.getAttribute("class") ? "." + e.getAttribute("class") : ""}`);
          }
          // texte hors du viewBox (cotes des faces, étiquettes des calepinages)
          const vb = svg.viewBox.baseVal;
          if (!vb || !vb.width) continue;
          const versSvg = svg.getScreenCTM().inverse();
          for (const tx of svg.querySelectorAll("text")) {
            if (!tx.checkVisibility() || !tx.textContent.trim()) continue;
            const b = tx.getBBox(), m = versSvg.multiply(tx.getScreenCTM());
            const pts = [[b.x, b.y], [b.x + b.width, b.y + b.height]].map(([x, y]) => {
              const p = svg.createSVGPoint(); p.x = x; p.y = y; return p.matrixTransform(m);
            });
            const g = 0.6;
            if (Math.min(pts[0].x, pts[1].x) < vb.x - g || Math.max(pts[0].x, pts[1].x) > vb.x + vb.width + g
                || Math.min(pts[0].y, pts[1].y) < vb.y - g || Math.max(pts[0].y, pts[1].y) > vb.y + vb.height + g)
              dehors.push(tx.textContent.trim().slice(0, 30));
          }
        }
        return {n: svgs.length, noirs: [...new Set(noirs)], dehors: [...new Set(dehors)]};
      }, vue);
      verifier(r.n > 0, `dessins de ${vue} : aucun`);
      verifier(r.noirs.length === 0, `dessins de ${vue} : aplat noir ${JSON.stringify(r.noirs.slice(0, 8))}`);
      verifier(r.dehors.length === 0, `dessins de ${vue} : texte hors du viewBox ${JSON.stringify(r.dehors.slice(0, 8))}`);
    }
  });

  // ------------------------------------------------------------------ 7. Achats : totaux, lien vers le meuble bas
  await partie("achats", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#achats");
    await vueAffichee(page, "achats", "achats");
    const total = await page.evaluate(() => document.querySelector('section[data-vue="achats"]').textContent.replace(/\s+/g, " "));
    for (const m of ["179,82 €", "296,82 €", "476,64 €", "Total du meuble haut"]) verifier(total.includes(m), `achats : « ${m} » absent`);
    const lien = page.locator('section[data-vue="achats"] a:has-text("Meuble bas")').first();
    const [reponse] = await Promise.all([page.waitForNavigation(), lien.click()]);
    const ici = await page.evaluate(() => location.pathname + location.hash);
    verifier(ici === "/sdb/meuble-bas/#achats" && reponse && reponse.status() === 200,
             `achats : « Meuble bas » mène à ${ici} (${reponse && reponse.status()})`);
  });

  // ------------------------------------------------------------------ 8. anciennes adresses
  await partie("anciennes adresses", async () => {
    const suivre = async (entree, chemin) => {
      await page.goto("about:blank");
      await page.goto(BASE + entree);
      await attendre(page, c => location.pathname === c && document.readyState === "complete", chemin, `${entree} : n'arrive pas à ${chemin}`);
      return page.evaluate(() => ({chemin: location.pathname, hash: location.hash}));
    };
    const H = "/sdb/meuble-haut/";
    const cas = [
      ["/sdb-meuble-haut.html#iso", H, "#plans?k=iso"],
      ["/sdb-meuble-haut.html#montage", H, "#montage"],
      ["/sdb-meuble-haut.html#etape-9", H, "#montage"],
      ["/sdb-meuble-haut.html#op-10-2", H, "#montage"],
      ["/sdb-meuble-haut.html#comment-percer", H, "#montage"],
      ["/sdb-meuble-haut.html#fixer-haut", H, "#montage"],
      ["/sdb-meuble-haut.html#fiches", H, "#decoupe"],
      ["/sdb-meuble-haut.html#decoupe", H, "#decoupe"],
      ["/sdb-meuble-haut.html#achats", H, "#achats"],
      ["/sdb-meuble-haut.html#materiaux", H, "#explication"],
      ["/sdb-meuble-haut.html#changements", H + "historique.html", ""],
      ["/sdb-meuble-haut.html#inconnue", H, ""],
      ["/sdb-meuble-haut.html", H, ""],
      ["/sdb-meuble-achats.html#haut-seul", H, "#achats"],
      ["/sdb-meuble-achats.html#deux-meubles", H, "#achats"],
      ["/sdb-meuble-achats.html", H, "#achats"],
      ["/sdb-meuble-achats.html#bas", "/sdb/meuble-bas/", "#achats"],
      ["/sdb-meuble-achats.html#changements", "/sdb/meuble-bas/historique.html", ""],
    ];
    for (const [entree, chemin, hash] of cas) {
      const r = await suivre(entree, chemin);
      verifier(r.chemin === chemin && r.hash === hash, `${entree} : ${JSON.stringify(r)} au lieu de ${chemin}${hash}`);
    }
  });

  // ------------------------------------------------------------------ 9. historique et versions figées
  await partie("historique", async () => {
    await ouvrir(page, DOC + "historique.html");
    const h = await page.evaluate(() => {
      const li = [...document.querySelectorAll("ol.fil li")];
      return {n: li.length, premiere: li.length ? li[0].textContent : "",
              figees: [...document.querySelectorAll('a[href*="archives/"]')].map(a => a.href)};
    });
    verifier(h.n === 2, `historique : ${h.n} entrées au lieu de 2`);
    verifier(h.premiere.includes("V6.4"), `historique : la première entrée n'est pas en V6.4 : « ${h.premiere.slice(0, 60)} »`);
    verifier(h.figees.length === 8, `historique : ${h.figees.length} versions figées au lieu de 8`);
    for (const u of h.figees) {
      const statut = await page.evaluate(async u => (await fetch(u)).status, u);
      verifier(statut === 200, `historique : ${u} en statut ${statut}`);
    }
  });

  // ------------------------------------------------------------------ 10. sans JavaScript
  await partie("sans JavaScript", async () => {
    const sansJs = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      await sansPolices(sansJs);
      const p = await sansJs.newPage();
      await preparer(p);
      for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
        await p.setViewportSize({width: largeur, height: hauteur});
        await p.goto(DOC);
        const s = await p.evaluate(() => {
          const vues = [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility())
            .map(x => { const r = x.getBoundingClientRect(); return [x.dataset.vue, Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; });
          const texte = document.querySelector("#contenu").innerText;
          return {classe: document.documentElement.className, vues,
                  titres: ["Pièces", "Comment percer", "Les deux meubles", "Matériaux possibles"].filter(x => texte.includes(x))};
        });
        const suite = s.vues.every((v, i) => i === 0 || v[1] >= s.vues[i - 1][2] - 1);
        verifier(s.classe.includes("sans-js") && egal(s.vues.map(v => v[0]), VUES) && suite && s.titres.length === 4,
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
