/* Personnaliser : choix d'une teinte (variable CSS, pentes du filtre, pastille), mémorisation partagée entre les
   variantes, rendus recolorés (y compris le clone de la comparaison), « Valeurs d'origine », sans localStorage ; puis
   les options « choix » table et bois (html[data-options], éléments data-si, zones et fiches de meuble, images par
   valeur et note d'une image absente, script de tête, comparaison, sans JavaScript, stockage refusé, mobile).
   Lancé par tests/navigateur/lancer.sh, qui ouvre la racine du site d'essai avant d'appeler ce script. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/essai/amenagement/`;
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };

  const preparer = async p => {
    p.on("console", m => { if (m.type() === "error") erreurs.push(`console : ${m.text()}`); });
    p.on("pageerror", e => erreurs.push(`page : ${e.message}`));
    p.setDefaultTimeout(3000);
    await p.emulateMedia({reducedMotion: "reduce"});
  };
  const ouvrir = async (p, adresse) => { await p.goto("about:blank"); await p.goto(adresse); };
  const attendre = async (p, condition, message) => {
    try { await p.waitForFunction(condition, null, {timeout: 2000}); } catch (e) { echecs.push(message); }
  };

  // ce que montre la page : variable CSS, pentes du filtre, pastille, bouton choisi, panneau
  const lire = p => p.evaluate(() => {
    const pastille = document.querySelector("#n-options"), panneau = document.querySelector("#panneau-options");
    const pente = c => +document.querySelector(`#filtre-teinte feFunc${c}`).getAttribute("slope");
    return {
      css: getComputedStyle(document.documentElement).getPropertyValue("--teinte").trim().toLowerCase(),
      pentes: ["R", "G", "B"].map(pente),
      pastille: pastille.hidden ? "" : pastille.textContent,
      etiquette: pastille.getAttribute("aria-label"),
      choisi: [...document.querySelectorAll("#panneau-options section[data-o='teinte'] [data-v][aria-pressed='true']")].map(b => b.dataset.v),
      ouvert: panneau.checkVisibility(),
      info: (panneau.querySelector(".info") || {}).textContent || "",
      stocke: localStorage.getItem("plans:essai/amenagement:teinte"),
    };
  });
  const pentes = hex => [1, 3, 5].map(i => parseInt(hex.substr(i, 2), 16) / 255 / 0.8);
  const proches = (a, b) => a.length === b.length && a.every((x, i) => Math.abs(x - b[i]) < 0.001);
  const calque = (p, selecteur) => p.evaluate(s => {
    const i = document.querySelector(s);
    if (!i) return null;
    const c = getComputedStyle(i);
    return {filtre: c.filter, masque: c.maskImage || c.webkitMaskImage};
  }, selecteur);
  const ouvrirPanneau = async p => { await p.click("#c-options"); await attendre(p, () => document.querySelector("#panneau-options").checkVisibility(), "le panneau ne s'ouvre pas"); };

  await page.context().route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                             r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  await preparer(page);

  try {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#camera");
    await page.evaluate(() => localStorage.clear());
    await ouvrir(page, DOC + "#camera");

    // Valeur d'origine : v1, pas de pastille, panneau fermé
    let l = await lire(page);
    verifier(l.css === "#eeebe3" && proches(l.pentes, pentes("#EEEBE3")) && l.pastille === "" && !l.ouvert,
             `origine : ${JSON.stringify(l)}`);

    // Le panneau : groupes, boutons, sans case à cocher, « Valeurs d'origine »
    await ouvrirPanneau(page);
    const p = await page.evaluate(() => {
      const f = document.querySelector("#panneau-options");
      return {titre: f.querySelector("h2").textContent, groupes: [...f.querySelectorAll("h4")].map(x => x.textContent),
              valeurs: [...f.querySelectorAll('section[data-o="teinte"] [data-v]')].map(b => b.dataset.v), cases: f.querySelectorAll("input").length,
              origine: [...f.querySelectorAll("button")].some(b => b.textContent.trim() === "Valeurs d'origine"),
              dialogue: f.getAttribute("role"), focus: document.activeElement.className};
    });
    verifier(p.titre === "Personnaliser" && JSON.stringify(p.groupes) === JSON.stringify(["Clairs", "Verts", "Ocres"]) &&
             JSON.stringify(p.valeurs) === JSON.stringify(["v1", "v2", "v3"]) && p.cases === 0 && p.origine && p.dialogue === "dialog",
             `panneau : ${JSON.stringify(p)}`);
    verifier(/fermer/.test(p.focus), `panneau : le focus n'entre pas dans le panneau (${p.focus})`);

    // Choisir v2 : variable, pentes, pastille, info, mémoire
    await page.click('#panneau-options [data-v="v2"]');
    l = await lire(page);
    verifier(l.css === "#a9b8a0", `v2 : --teinte = ${l.css}`);
    verifier(proches(l.pentes, pentes("#A9B8A0")), `v2 : pentes ${l.pentes}, attendu ${pentes("#A9B8A0")}`);
    verifier(l.pastille === "1" && /1 option/.test(l.etiquette || ""), `v2 : pastille « ${l.pastille} », étiquette « ${l.etiquette} »`);
    verifier(JSON.stringify(l.choisi) === '["v2"]' && l.info.includes("Sauge") && l.info.includes("peinture seulement"),
             `v2 : choisi ${l.choisi}, info « ${l.info} »`);
    verifier(l.stocke === JSON.stringify("v2"), `v2 : mémoire ${l.stocke}`);

    // Rendu recoloré : le calque porte le filtre et le masque
    let c = await calque(page, 'section[data-vue="camera"] .element:not(.b) img.calque');
    verifier(c && c.filtre.includes("filtre-teinte") && c.masque.includes("svg+xml"), `calque : ${JSON.stringify(c)}`);

    // Échap ferme le panneau et rend le focus à « Personnaliser »
    await page.keyboard.press("Escape");
    verifier(!(await lire(page)).ouvert, "Échap ne ferme pas le panneau");
    verifier(await page.evaluate(() => document.activeElement.id) === "c-options", "le focus ne revient pas sur #c-options");
    await ouvrirPanneau(page);
    await page.mouse.click(20, 500);   // hors du panneau : le voile
    verifier(!(await lire(page)).ouvert, "le voile ne ferme pas le panneau");

    // Partagé entre les variantes, après rechargement
    await ouvrir(page, DOC + "b.html#camera");
    l = await lire(page);
    verifier(l.css === "#a9b8a0" && l.pastille === "1" && proches(l.pentes, pentes("#A9B8A0")), `variante B : ${JSON.stringify(l)}`);
    await ouvrirPanneau(page);
    verifier(JSON.stringify((await lire(page)).choisi) === '["v2"]', "variante B : v2 n'est pas coché dans le panneau");
    await page.keyboard.press("Escape");

    // Comparaison : le clone de l'autre variante est recoloré aussi
    await ouvrir(page, DOC + "#camera?c=b");
    await attendre(page, () => document.querySelector('section[data-vue="camera"] .element.b img.calque'), "comparaison : pas de clone");
    c = await calque(page, 'section[data-vue="camera"] .element.b img.calque');
    verifier(c && c.filtre.includes("filtre-teinte") && c.masque.includes("svg+xml"), `clone : ${JSON.stringify(c)}`);
    const dans = await page.evaluate(() => {
      const i = document.querySelector('section[data-vue="camera"] .element.b img.calque');
      return i.checkVisibility() && i.getBoundingClientRect().width > 10;
    });
    verifier(dans, "clone : le calque n'est pas visible");

    // Valeurs d'origine
    await ouvrirPanneau(page);
    await page.click("#panneau-options >> text=Valeurs d'origine");
    l = await lire(page);
    verifier(l.css === "#eeebe3" && proches(l.pentes, pentes("#EEEBE3")) && l.pastille === "" &&
             JSON.stringify(l.choisi) === '["v1"]', `origine rendue : ${JSON.stringify(l)}`);
    await ouvrir(page, DOC + "b.html#camera");
    l = await lire(page);
    verifier(l.css === "#eeebe3" && l.pastille === "", `origine après rechargement : ${JSON.stringify(l)}`);

    // Une valeur mémorisée inconnue donne la valeur d'origine
    await page.evaluate(() => localStorage.setItem("plans:essai/amenagement:teinte", JSON.stringify("zzz")));
    await ouvrir(page, DOC + "#camera");
    l = await lire(page);
    verifier(l.css === "#eeebe3" && l.pastille === "", `valeur inconnue : ${JSON.stringify(l)}`);
    await page.evaluate(() => localStorage.clear());

    // Sans localStorage : la valeur d'origine s'affiche, le choix tient le temps de la page, sans erreur
    const privee = await page.context().newPage();
    await preparer(privee);
    await privee.addInitScript(() => {
      const refus = () => { throw new DOMException("stockage refusé", "SecurityError"); };
      Storage.prototype.getItem = refus;
      Storage.prototype.setItem = refus;
    });
    await privee.setViewportSize({width: 1440, height: 900});
    await privee.goto(DOC + "#camera");
    const lirePrivee = () => privee.evaluate(() => ({
      css: getComputedStyle(document.documentElement).getPropertyValue("--teinte").trim().toLowerCase(),
      pastille: document.querySelector("#n-options").hidden ? "" : document.querySelector("#n-options").textContent}));
    let q = await lirePrivee();
    verifier(q.css === "#eeebe3" && q.pastille === "", `sans localStorage : ${JSON.stringify(q)}`);
    await privee.click("#c-options");
    await privee.click('#panneau-options [data-v="v3"]');
    q = await lirePrivee();
    verifier(q.css === "#b5735a" && q.pastille === "1", `sans localStorage, après choix : ${JSON.stringify(q)}`);
    await privee.close();

    // Mobile : feuille basse, pas de défilement horizontal
    await page.setViewportSize({width: 390, height: 844});
    await ouvrir(page, DOC + "#camera");
    await ouvrirPanneau(page);
    const m = await page.evaluate(() => {
      const r = document.querySelector("#panneau-options").getBoundingClientRect();
      return {bas: r.bottom, gauche: r.left, droite: r.right, h: innerHeight, l: innerWidth, defil: document.documentElement.scrollWidth};
    });
    verifier(Math.abs(m.bas - m.h) <= 1 && m.gauche >= 0 && m.droite <= m.l && m.defil <= m.l, `mobile : ${JSON.stringify(m)}`);
    // feuille défilée pas à pas jusqu'en bas : l'en-tête collant (titre, fermer) reste au-dessus de la ligne .info
    // collante du nuancier ; le bouton de fermeture est l'élément au point de son centre à chaque pas
    const enTeteDessus = p => p.evaluate(async () => {
      const f = document.querySelector("#panneau-options"), b = f.querySelector(".fermer"), max = f.scrollHeight - f.clientHeight;
      const recouvert = [];
      for (let y = 0; ; y = Math.min(y + 8, max)) {
        f.scrollTop = y;
        await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
        const r = b.getBoundingClientRect(), ici = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        if (!ici || !b.contains(ici)) recouvert.push(`${y}:${ici ? ici.className.baseVal ?? ici.className : "rien"}`);
        if (y >= max) break;
      }
      const fin = f.scrollTop;
      f.scrollTop = 0;
      return {max, fin, recouvert};
    });
    let et = await enTeteDessus(page);
    verifier(et.recouvert.length === 0, `mobile, feuille défilée : l'en-tête est recouvert ${JSON.stringify(et)}`);

    // ------------------------------------------------------------------ options « choix » : table et bois
    // vus(p, [sélecteurs]) : pour chacun, true (montré), false (caché) ou null (absent : l'essai échoue, jamais à vide).
    // checkVisibility() seul ne suffit pas : Chromium le dit vrai pour un <g> de SVG en display:none (et ses enfants)
    const vus = (p, sels) => p.evaluate(s => Object.fromEntries(s.map(x => {
      const e = document.querySelector(x);
      if (!e) return [x, null];
      let montre = e.checkVisibility();
      for (let a = e; a && montre; a = a.parentElement) if (getComputedStyle(a).display === "none") montre = false;
      return [x, montre];
    })), sels);
    const tous = (v, attendu) => Object.entries(attendu).every(([s, b]) => v[s] === b);
    const etatHtml = p => p.evaluate(() => document.documentElement.dataset.options);
    const cliquerValeur = async (p, o, code) => {
      if (!(await p.evaluate(() => document.querySelector("#panneau-options").checkVisibility()))) await ouvrirPanneau(p);
      await p.click(`#panneau-options section[data-o="${o}"] [data-v="${code}"]`);
    };
    const fermerPanneau = async p => {
      if (await p.evaluate(() => document.querySelector("#panneau-options").checkVisibility())) await p.keyboard.press("Escape");
    };
    const aller = async (p, hash) => {
      await p.evaluate(h => { location.hash = h; }, hash);
      try { await p.waitForFunction(h => document.documentElement.dataset.vue === h.slice(1).split("?")[0], hash, {timeout: 2000}); }
      catch (e) { echecs.push(`aller à ${hash} : la vue ne suit pas`); }
    };
    const PLAN = 'section[data-vue="plan"]', CAM = 'section[data-vue="camera"] .element:not(.b)';
    const COUPE_A = 'section[data-vue="coupes"] .element[data-k="A"]:not(.b)';
    const Q = `${PLAN} g[data-si="table:quotidien"]`, O = `${PLAN} g[data-si="table:ouverte"]`, COMBI = `${PLAN} circle.combi`;
    const IMG = code => `${CAM} img[data-si="bois:${code}"]:not(.calque)`, NOTE = `${CAM} .note-rendu`;
    const ORIGINE = "table:quotidien bois:chene";
    const panneauChoix = p => p.evaluate(() => {
      const f = document.querySelector("#panneau-options"), s = id => f.querySelector(`section[data-o="${id}"]`);
      const pastille = document.querySelector("#n-options");
      return {
        sansRendu: ["table", "bois"].map(id => { const r = s(id).querySelector(".sans-rendu"); return r ? r.checkVisibility() : null; }),
        texteSansRendu: (s("table").querySelector(".sans-rendu") || {}).textContent || "",
        choisis: [...f.querySelectorAll("[data-v][aria-pressed='true']")].map(b => `${b.closest("section").dataset.o}:${b.dataset.v}`),
        pastille: pastille.hidden ? "" : pastille.textContent, etiquette: pastille.getAttribute("aria-label"),
      };
    });
    const ficheMeuble = p => p.evaluate(() => {
      const s = document.querySelector('section[data-vue="plan"]'), ici = [...s.querySelectorAll("rect.zone.ici")];
      return {hash: location.hash, nom: s.querySelector(".fiche-nom").textContent,
              cotes: (s.querySelector(".fiche-meuble .cotes") || {}).textContent || "",
              ici: ici.map(z => `${z.dataset.meuble}/${z.dataset.si || ""}`)};
    });

    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#camera");
    await page.evaluate(() => localStorage.clear());
    await ouvrir(page, DOC + "#camera");

    // Origine : l'état d'origine sur <html>, la table du quotidien, l'image en chêne
    verifier(await etatHtml(page) === ORIGINE, `choix, origine : data-options « ${await etatHtml(page)} »`);
    let v = await vus(page, [IMG("chene"), IMG("noyer"), IMG("frene"), NOTE]);
    verifier(tous(v, {[IMG("chene")]: true, [IMG("noyer")]: false, [IMG("frene")]: false, [NOTE]: false}),
             `choix, origine, caméra : ${JSON.stringify(v)}`);
    await aller(page, "#plan");
    v = await vus(page, [Q, O, COMBI]);
    verifier(tous(v, {[Q]: true, [O]: false, [COMBI]: false}), `choix, origine, plan : ${JSON.stringify(v)}`);

    // Panneau : trois sections dans l'ordre ; pastille de couleur pour le bois seulement ; pas de ligne .info ; portées
    await ouvrirPanneau(page);
    const pc = await page.evaluate(() => {
      const f = document.querySelector("#panneau-options"), s = id => f.querySelector(`section[data-o="${id}"]`);
      return {
        ordre: [...f.querySelectorAll("section[data-o]")].map(x => x.dataset.o),
        table: [...s("table").querySelectorAll("button[data-v]")].map(b => `${b.dataset.v}:${b.querySelectorAll("i").length}:${b.textContent}`),
        bois: [...s("bois").querySelectorAll("button[data-v]")].map(b => {
          const i = b.querySelector("i");
          return `${b.dataset.v}:${i ? getComputedStyle(i).backgroundColor : "-"}:${b.textContent}`;
        }),
        infos: s("table").querySelectorAll(".info").length + s("bois").querySelectorAll(".info").length,
        portees: ["table", "bois"].map(id => [...s(id).querySelectorAll(".remarque:not(.sans-rendu)")]
          .filter(x => x.checkVisibility()).map(x => x.textContent)),
        grilles: ["table", "bois"].map(id => s(id).querySelectorAll(".choix-opt").length),
        // la remarque « pas encore rendu » est dans une région annoncée, présente et montrée dès l'ouverture
        annonces: ["table", "bois"].map(id => {
          const r = s(id).querySelector(".sans-rendu"), z = r && r.parentElement;
          return !!z && z.getAttribute("role") === "status" && z !== s(id) && z.checkVisibility();
        }),
      };
    });
    verifier(JSON.stringify(pc.ordre) === '["teinte","table","bois"]', `choix, panneau : ordre ${pc.ordre}`);
    verifier(JSON.stringify(pc.table) === '["quotidien:0:Au quotidien","ouverte:0:Ouverte"]', `choix, panneau : table ${pc.table}`);
    verifier(JSON.stringify(pc.bois) === JSON.stringify(["chene:rgb(176, 122, 69):Chêne", "noyer:rgb(107, 70, 48):Noyer",
                                                         "frene:rgb(217, 191, 146):Frêne"]), `choix, panneau : bois ${pc.bois}`);
    verifier(pc.infos === 0 && JSON.stringify(pc.grilles) === "[1,1]", `choix, panneau : ${pc.infos} .info, grilles ${pc.grilles}`);
    verifier(JSON.stringify(pc.annonces) === "[true,true]", `choix, panneau : remarque hors d'une région role="status" ${pc.annonces}`);
    verifier(JSON.stringify(pc.portees) === JSON.stringify([["Visible sur le plan et les coupes ; les rendus montrent la table du quotidien."],
                                                            ["Visible sur les rendus ; le plan et les coupes ne changent pas."]]),
             `choix, panneau : portées ${JSON.stringify(pc.portees)}`);
    let pa = await panneauChoix(page);
    verifier(JSON.stringify(pa.sansRendu) === "[false,false]" && pa.pastille === "" &&
             JSON.stringify(pa.choisis) === '["teinte:v1","table:quotidien","bois:chene"]', `choix, panneau à l'origine : ${JSON.stringify(pa)}`);

    // « Ouverte » : pastille, remarque « pas encore rendu », mémoire ; le plan et la coupe A suivent sans rechargement
    await cliquerValeur(page, "table", "ouverte");
    pa = await panneauChoix(page);
    verifier(pa.pastille === "1" && JSON.stringify(pa.sansRendu) === "[true,false]" &&
             pa.texteSansRendu === "Pas encore rendu : les rendus ne montrent pas ce choix." &&
             JSON.stringify(pa.choisis) === '["teinte:v1","table:ouverte","bois:chene"]', `ouverte, panneau : ${JSON.stringify(pa)}`);
    verifier(await page.evaluate(() => localStorage.getItem("plans:essai/amenagement:table")) === JSON.stringify("ouverte"),
             "ouverte : mémoire plans:essai/amenagement:table");
    verifier(await etatHtml(page) === "table:ouverte bois:chene", `ouverte : data-options « ${await etatHtml(page)} »`);
    v = await vus(page, [Q, O, COMBI]);
    verifier(tous(v, {[Q]: false, [O]: true, [COMBI]: false}), `ouverte, plan : ${JSON.stringify(v)}`);
    await fermerPanneau(page);
    await aller(page, "#coupes?k=A");
    const AQ = `${COUPE_A} g[data-si="table:quotidien"]`, AO = `${COUPE_A} g[data-si="table:ouverte"]`;
    const FA = 'section[data-vue="coupes"] .fiche-element[data-k="A"] p[data-si="table:ouverte"]';
    v = await vus(page, [AQ, AO, FA]);
    verifier(tous(v, {[AQ]: false, [AO]: true, [FA]: true}), `ouverte, coupe A : ${JSON.stringify(v)}`);
    verifier(await page.evaluate(s => document.querySelector(s).textContent, FA) === "Table ouverte.", "ouverte, coupe A : texte de la fiche");

    // Zone : seule la zone de l'état se touche ; sa fiche dit 25 cm ; une seule zone .ici
    await aller(page, "#plan");
    const zoneVue = await page.evaluate(() => {
      const z = [...document.querySelectorAll('section[data-vue="plan"] rect.zone[data-meuble="table"]')].filter(x => x.checkVisibility());
      if (z.length !== 1) return {n: z.length};
      const b = z[0].getBoundingClientRect();
      return {n: 1, si: z[0].dataset.si, x: b.left + b.width / 2, y: b.top + b.height / 2};
    });
    verifier(zoneVue.n === 1 && zoneVue.si === "table:ouverte", `ouverte, zones de la table : ${JSON.stringify(zoneVue)}`);
    if (zoneVue.n === 1) await page.mouse.click(zoneVue.x, zoneVue.y);
    let fm = await ficheMeuble(page);
    verifier(fm.hash === "#plan?k=table" && fm.nom === "Table" && fm.cotes === "25 cm" &&
             JSON.stringify(fm.ici) === '["table/table:ouverte"]', `ouverte, fiche de la table : ${JSON.stringify(fm)}`);

    // Au clavier : depuis le banc, Tab va à la zone de la table montrée, puis quitte les zones (la cachée n'est pas atteinte)
    await page.focus(`${PLAN} rect.zone[data-meuble="0"]`);
    const parcours = [];
    for (let i = 0; i < 2; i++) {
      await page.keyboard.press("Tab");
      parcours.push(await page.evaluate(() => {
        const a = document.activeElement;
        return a.matches("rect.zone") ? `zone ${a.dataset.meuble}/${a.dataset.si || ""}` : "autre";
      }));
    }
    verifier(JSON.stringify(parcours) === '["zone table/table:ouverte","autre"]', `ouverte, Tab : ${parcours}`);

    // Repasser en « quotidien » fiche ouverte : la fiche suit la nouvelle emprise
    await cliquerValeur(page, "table", "quotidien");
    fm = await ficheMeuble(page);
    verifier(fm.hash === "#plan?k=table" && fm.cotes === "15 cm" && JSON.stringify(fm.ici) === '["table/table:quotidien"]',
             `quotidien, fiche ouverte : ${JSON.stringify(fm)}`);
    await fermerPanneau(page);

    // Combinaison : le cercle ne se montre qu'avec « ouverte » et « noyer » ; l'image suit le bois
    await cliquerValeur(page, "table", "ouverte");
    await cliquerValeur(page, "bois", "noyer");
    verifier((await vus(page, [COMBI]))[COMBI] === true, "ouverte et noyer : le cercle n'est pas montré");
    await cliquerValeur(page, "table", "quotidien");
    verifier((await vus(page, [COMBI]))[COMBI] === false, "noyer seul : le cercle est montré");
    await fermerPanneau(page);
    await aller(page, "#camera");
    v = await vus(page, [IMG("chene"), IMG("noyer"), IMG("frene"), NOTE]);
    verifier(tous(v, {[IMG("chene")]: false, [IMG("noyer")]: true, [IMG("frene")]: false, [NOTE]: false}),
             `noyer, caméra : ${JSON.stringify(v)}`);
    await cliquerValeur(page, "bois", "frene");
    v = await vus(page, [IMG("chene"), IMG("noyer"), IMG("frene"), NOTE]);
    verifier(tous(v, {[IMG("chene")]: false, [IMG("noyer")]: false, [IMG("frene")]: true, [NOTE]: true}),
             `frêne, caméra : ${JSON.stringify(v)}`);
    verifier(await page.evaluate(s => document.querySelector(s).textContent, NOTE) === "Frêne : pas encore rendu, image en Chêne",
             "frêne : texte de la note");
    pa = await panneauChoix(page);
    verifier(JSON.stringify(pa.sansRendu) === "[false,true]", `frêne, panneau : ${JSON.stringify(pa)}`);

    // Pastille : trois options changées, puis « Valeurs d'origine » remet tout
    await page.click("#panneau-options >> text=Valeurs d'origine");
    await cliquerValeur(page, "teinte", "v2");
    await cliquerValeur(page, "table", "ouverte");
    await cliquerValeur(page, "bois", "noyer");
    pa = await panneauChoix(page);
    verifier(pa.pastille === "3" && pa.etiquette === "3 options modifiées", `trois options : ${JSON.stringify(pa)}`);
    await page.click("#panneau-options >> text=Valeurs d'origine");
    pa = await panneauChoix(page);
    l = await lire(page);
    verifier(pa.pastille === "" && await etatHtml(page) === ORIGINE && l.css === "#eeebe3" &&
             JSON.stringify(pa.choisis) === '["teinte:v1","table:quotidien","bois:chene"]', `Valeurs d'origine : ${JSON.stringify(pa)}`);
    v = await vus(page, [IMG("chene"), IMG("noyer")]);
    verifier(tous(v, {[IMG("chene")]: true, [IMG("noyer")]: false}), `Valeurs d'origine, caméra : ${JSON.stringify(v)}`);
    await fermerPanneau(page);

    // Script de tête, sans site.js : l'état mémorisé est posé au chargement ; une valeur inconnue donne l'origine
    const tete = await page.context().newPage();
    tete.on("console", m => { if (m.type() === "error" && !/Failed to load resource/.test(m.text())) erreurs.push(`tête, console : ${m.text()}`); });
    tete.on("pageerror", e => erreurs.push(`tête, page : ${e.message}`));
    tete.setDefaultTimeout(3000);
    await tete.setViewportSize({width: 1440, height: 900});
    await tete.route("**/commun/site.js", r => r.abort());
    await tete.goto(DOC + "#plan");
    await tete.evaluate(() => localStorage.setItem("plans:essai/amenagement:table", JSON.stringify("ouverte")));
    await ouvrir(tete, DOC + "#plan");
    // site.js n'a pas tourné : le panneau est resté vide
    const lireTete = async () => ({...await tete.evaluate(() => ({
      siteJs: document.querySelector("#panneau-options").children.length > 0, etat: document.documentElement.dataset.options})),
      ...await vus(tete, [Q, O])});
    let t = await lireTete();
    verifier(!t.siteJs && t.etat === "table:ouverte bois:chene" && t[Q] === false && t[O] === true,
             `script de tête, ouverte mémorisée : ${JSON.stringify(t)}`);
    await tete.evaluate(() => localStorage.setItem("plans:essai/amenagement:table", JSON.stringify("zzz")));
    await ouvrir(tete, DOC + "#plan");
    t = await lireTete();
    verifier(!t.siteJs && t.etat === ORIGINE && t[Q] === true && t[O] === false, `script de tête, valeur inconnue : ${JSON.stringify(t)}`);
    await tete.evaluate(() => localStorage.clear());
    await tete.close();

    // Comparaison : le clone suit l'état, dessin et image, et le suit encore quand on change de valeur
    await page.evaluate(() => {
      localStorage.setItem("plans:essai/amenagement:table", JSON.stringify("ouverte"));
      localStorage.setItem("plans:essai/amenagement:bois", JSON.stringify("noyer"));
    });
    await ouvrir(page, DOC + "#coupes?k=A&c=b");
    await attendre(page, () => document.querySelector('section[data-vue="coupes"] .element.b'), "comparaison, coupe A : pas de clone");
    const BQ = 'section[data-vue="coupes"] .element.b g[data-si="table:quotidien"]', BO = 'section[data-vue="coupes"] .element.b g[data-si="table:ouverte"]';
    v = await vus(page, [BQ, BO]);
    verifier(tous(v, {[BQ]: false, [BO]: true}), `comparaison, coupe A : ${JSON.stringify(v)}`);
    await ouvrir(page, DOC + "#camera?c=b");
    await attendre(page, () => document.querySelector('section[data-vue="camera"] .element.b'), "comparaison, caméra : pas de clone");
    const BIMG = code => `section[data-vue="camera"] .element.b img[data-si="bois:${code}"]:not(.calque)`;
    const BNOTE = 'section[data-vue="camera"] .element.b .note-rendu';
    v = await vus(page, [BIMG("chene"), BIMG("noyer")]);
    verifier(tous(v, {[BIMG("chene")]: false, [BIMG("noyer")]: true}), `comparaison, caméra en noyer : ${JSON.stringify(v)}`);
    await cliquerValeur(page, "bois", "frene");
    await fermerPanneau(page);
    v = await vus(page, [BIMG("noyer"), BIMG("frene"), BNOTE, NOTE]);
    verifier(tous(v, {[BIMG("noyer")]: false, [BIMG("frene")]: true, [BNOTE]: true, [NOTE]: true}),
             `comparaison, caméra en frêne : ${JSON.stringify(v)}`);
    // les notes se lisent : celle de la base à gauche du rideau, sous les outils, celle du clone à droite, dans la scène
    const notesRangees = p => p.evaluate(([a, b]) => {
      const scene = document.querySelector('section[data-vue="camera"] .scene'), s = scene.getBoundingClientRect(), m = s.left + s.width / 2;
      const ra = document.querySelector(a).getBoundingClientRect(), rb = document.querySelector(b).getBoundingClientRect();
      const ro = scene.querySelector(".outils").getBoundingClientRect();
      const croise = (x, y) => x.left < y.right && y.left < x.right && x.top < y.bottom && y.top < x.bottom;
      return {base: ra.right <= m, clone: rb.left >= m, sousOutils: !croise(ra, ro) && !croise(rb, ro),
              dedans: ra.left >= s.left && rb.right <= s.right && ra.top >= s.top && rb.top >= s.top};
    }, [NOTE, BNOTE]);
    let rangees = await notesRangees(page);
    verifier(rangees.base && rangees.clone && rangees.sousOutils && rangees.dedans, `comparaison, notes à 1440 px : ${JSON.stringify(rangees)}`);
    // rideau poussé près d'un bord : chaque note garde la hauteur d'une ligne et reste dans son côté du rideau
    const notesAuRideau = p => p.evaluate(([a, b]) => {
      const scene = document.querySelector('section[data-vue="camera"] .scene'), s = scene.getBoundingClientRect();
      const m = s.left + s.width * (parseFloat(scene.style.getPropertyValue("--pos")) || 50) / 100;
      const ra = document.querySelector(a).getBoundingClientRect(), rb = document.querySelector(b).getBoundingClientRect();
      return {pos: scene.style.getPropertyValue("--pos"), hauteurs: [ra.height, rb.height], base: ra.right <= m + 0.5, clone: rb.left >= m - 0.5};
    }, [NOTE, BNOTE]);
    const auMilieu = await notesAuRideau(page);
    await page.focus('section[data-vue="camera"] .poignee');
    for (const [touche, fois, bord] of [["ArrowLeft", 12, "gauche"], ["ArrowRight", 23, "droit"]]) {
      for (let i = 0; i < fois; i++) await page.keyboard.press(touche);
      const r = await notesAuRideau(page);
      verifier(r.hauteurs.every((h, i) => Math.abs(h - auMilieu.hauteurs[i]) < 0.5) && r.base && r.clone,
               `comparaison, rideau près du bord ${bord} : ${JSON.stringify(r)}, au milieu ${JSON.stringify(auMilieu.hauteurs)}`);
    }
    await page.setViewportSize({width: 390, height: 844});
    await ouvrir(page, DOC + "#camera?c=b");
    await attendre(page, () => document.querySelector('section[data-vue="camera"] .element.b'), "comparaison à 390 px : pas de clone");
    rangees = await notesRangees(page);
    verifier(rangees.base && rangees.clone && rangees.sousOutils && rangees.dedans, `comparaison, notes à 390 px : ${JSON.stringify(rangees)}`);
    await page.setViewportSize({width: 1440, height: 900});
    await page.evaluate(() => localStorage.clear());

    // Sans JavaScript : l'état d'origine écrit dans la page et le <style> de tête suffisent
    const sansJs = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      await sansJs.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
      const s = await sansJs.newPage();
      await preparer(s);
      await s.setViewportSize({width: 1440, height: 900});
      await s.goto(DOC);
      const SQ = `${PLAN} g[data-si="table:quotidien"]`, SO = `${PLAN} g[data-si="table:ouverte"]`;
      const SC = 'section[data-vue="camera"] img[data-si="bois:chene"]:not(.calque)', SN = 'section[data-vue="camera"] img[data-si="bois:noyer"]:not(.calque)';
      const r = {sansJs: await s.evaluate(() => document.documentElement.classList.contains("sans-js")), ...await vus(s, [SQ, SO, SC, SN])};
      verifier(r.sansJs && tous(r, {[SQ]: true, [SO]: false, [SC]: true, [SN]: false}), `sans JavaScript : ${JSON.stringify(r)}`);
    } finally {
      await sansJs.close();
    }

    // Stockage refusé : l'origine s'affiche, « ouverte » change le plan, sans erreur
    const refusee = await page.context().newPage();
    await preparer(refusee);
    await refusee.addInitScript(() => {
      const refus = () => { throw new DOMException("stockage refusé", "SecurityError"); };
      Storage.prototype.getItem = refus;
      Storage.prototype.setItem = refus;
    });
    await refusee.setViewportSize({width: 1440, height: 900});
    await refusee.goto(DOC + "#plan");
    v = await vus(refusee, [Q, O]);
    verifier(await etatHtml(refusee) === ORIGINE && tous(v, {[Q]: true, [O]: false}), `stockage refusé, origine : ${JSON.stringify(v)}`);
    await cliquerValeur(refusee, "table", "ouverte");
    v = await vus(refusee, [Q, O]);
    verifier(await etatHtml(refusee) === "table:ouverte bois:chene" && tous(v, {[Q]: false, [O]: true}),
             `stockage refusé, ouverte : ${JSON.stringify(v)}`);
    await refusee.close();

    // 390 px : un choix met la fiche du meuble à jour sans la déplier ni la replier ; « Valeurs d'origine » de même
    await page.setViewportSize({width: 390, height: 844});
    await page.evaluate(() => localStorage.clear());
    await ouvrir(page, DOC + "#plan?k=table");
    const ficheMobile = p => p.evaluate(() => {
      const f = document.querySelector('section[data-vue="plan"] .fiche');
      return {ouverte: f.classList.contains("ouverte"), etendue: f.querySelector(".fiche-tete").getAttribute("aria-expanded"),
              cotes: (f.querySelector(".fiche-meuble .cotes") || {}).textContent || ""};
    });
    const replier = async p => { await fermerPanneau(p); await p.click('section[data-vue="plan"] .fiche-tete'); };
    let fi = await ficheMobile(page);
    verifier(fi.ouverte && fi.cotes === "15 cm", `fiche à 390 px, au chargement : ${JSON.stringify(fi)}`);
    await replier(page);
    await cliquerValeur(page, "bois", "noyer");
    fi = await ficheMobile(page);
    verifier(!fi.ouverte && fi.etendue === "false", `fiche repliée, après « noyer » : ${JSON.stringify(fi)}`);
    await cliquerValeur(page, "table", "ouverte");
    fi = await ficheMobile(page);
    verifier(!fi.ouverte && fi.etendue === "false" && fi.cotes === "25 cm", `fiche repliée, après « ouverte » : ${JSON.stringify(fi)}`);
    await page.click("#panneau-options >> text=Valeurs d'origine");
    fi = await ficheMobile(page);
    verifier(!fi.ouverte && fi.cotes === "15 cm", `fiche repliée, après « Valeurs d'origine » : ${JSON.stringify(fi)}`);
    await replier(page);   // la déplie
    await cliquerValeur(page, "table", "ouverte");
    fi = await ficheMobile(page);
    verifier(fi.ouverte && fi.etendue === "true" && fi.cotes === "25 cm", `fiche ouverte, après « ouverte » : ${JSON.stringify(fi)}`);
    await fermerPanneau(page);
    await page.evaluate(() => localStorage.clear());

    // 390 px : le panneau a ses trois sections, sans défilement horizontal
    await page.setViewportSize({width: 390, height: 844});
    await ouvrir(page, DOC + "#plan");
    await ouvrirPanneau(page);
    await cliquerValeur(page, "table", "ouverte");
    et = await enTeteDessus(page);
    verifier(et.max > 0 && et.fin === et.max && et.recouvert.length === 0,
             `choix, mobile, feuille défilée jusqu'en bas : l'en-tête est recouvert ${JSON.stringify(et)}`);
    const mc = await page.evaluate(() => {
      const f = document.querySelector("#panneau-options"), r = f.getBoundingClientRect();
      return {sections: [...f.querySelectorAll("section[data-o]")].map(x => x.dataset.o),
              larges: [...f.querySelectorAll("section[data-o] button, section[data-o] .remarque")].filter(x => x.checkVisibility())
                .filter(x => x.getBoundingClientRect().right > r.right + 0.5).length,
              defil: document.documentElement.scrollWidth, l: innerWidth, panneau: f.scrollWidth <= f.clientWidth};
    });
    verifier(JSON.stringify(mc.sections) === '["teinte","table","bois"]' && mc.larges === 0 && mc.defil <= mc.l && mc.panneau,
             `choix, mobile : ${JSON.stringify(mc)}`);
    await page.evaluate(() => localStorage.clear());
  } catch (e) {
    echecs.push(`exception : ${e.message.split("\n")[0]}`);
  }

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
