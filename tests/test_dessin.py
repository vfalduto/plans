from commun import dessin as D


def test_sorties_identiques_a_l_entree():
    assert [
        D.virg(8.1),
        D.f(12.0),
        D.f(12.5),
        D.rect(0, 0, 10, 20, 'w'),
        D.text(5, 5, 'A-A'),
        D.cote_h(0, 264, -20),
        D.cote_v(0, 104, 300, '104'),
        D.degage((0, 245), (110, 245), '110'),
        D.coin_arrondi(85, 110, 170, 208, 25, 'cab'),
    ] == [
        '8,1',
        '12',
        '12.5',
        '<rect class="w" x="0" y="0" width="10" height="20"/>',
        '<text class="lbl" x="5" y="5" text-anchor="middle">A-A</text>',
        '<line class="dim" x1="0" y1="-20" x2="264" y2="-20"/><line class="dim" x1="0" y1="-23" x2="0" y2="-17"/><line class="dim" x1="264" y1="-23" x2="264" y2="-17"/><text class="dimt" x="132" y="-22.5" text-anchor="middle">264</text>',
        '<line class="dim" x1="300" y1="0" x2="300" y2="104"/><line class="dim" x1="297" y1="0" x2="303" y2="0"/><line class="dim" x1="297" y1="104" x2="303" y2="104"/><text class="dimt" x="297.5" y="52" text-anchor="middle" transform="rotate(-90 297.5 52)">104</text>',
        '<line class="pass" x1="0" y1="245" x2="110" y2="245"/><circle class="passm" cx="0" cy="245" r="1.3"/><circle class="passm" cx="110" cy="245" r="1.3"/><text class="passt" x="55" y="242" text-anchor="middle">110</text>',
        '<path class="cab" d="M110 170 L110 208 L85 208 L85 195 A25 25 0 0 1 110 170 Z"/>',
    ]
