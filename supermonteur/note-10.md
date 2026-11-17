# Étape 8 : note /10 face à la réf monteur (obligatoire, sauf B-roll + texte qui a sa grille du Copywriter)

```bash
python3 $S/score.py final.mp4          # ~10 s ; réf par défaut ref/FINAL.mp4 (client : sans réf) ; sort score/metrics.json, compare.jpg, hook.jpg
```
Regarder `score/compare.jpg` (haut = reel, bas = réf) et `score/hook.jpg`, puis noter chaque critère 0 / 0.5 / 1 (critère sans objet pour le style = retiré du total, note ramenée sur 10) :
1. **Hook** : dans les 3 premières s, quelque chose bouge ou claque (chiffre, zoom, B-roll). Pas 3 s de tête fixe.
2. **Dérush** : 0 blanc > 0.4 s (`blancs_sup_0.4s`), aucune coupe en milieu de phrase. Débit `mots_par_min` ≤ 240 (cible 165-195 pour un ton posé ; Victor Heras 158-192).
3. **Sous-titres** : 0 faute (relire), 1 bloc à la fois, mots forts en serif SEULS à l'écran, rien sur le cou. `car_par_s_max` ≤ 20 (Netflix, BBC) ; au-dessus, c'est le dérush qui est trop serré.
4. **Chiffres** : tête devant chaque chiffre, lisible, pas coupé par le cadre.
5. **Listes / pastilles** : lisibles, contenu de la personne, pas inventé.
6. **Rythme** : `plus_long_plan_fixe_s` ≤ celui de la réf + 2 s ; zooms qui alternent (le détecteur ne voit pas les zooms : vérifier à l'œil).
7. **B-rolls** : chacun montre EXACTEMENT ce qui est dit à cet instant ET est beau (net, vertical bien cadré, lumière propre). Un seul B-roll moyen = 0.5 ; deux = 0. Répartis régulièrement, même personne. Dans le doute : face cam.
8. **Musique** : émotionnelle, on l'ENTEND (musique seule mesurée avec Demucs : 15-17 dB sous la voix ; « il n'y a pas de musique » est arrivé avec un mix « OK »), pas celle du reel précédent.
9. **Son** : `lufs` entre -15 et -13, SFX discrets et calés. ≤ 1 SFX toutes les 4 s en moyenne, jamais 2 à moins de 1,5 s (`mix.py` affiche la liste gardée / sautée), 1 seul silence + riser. Plus de 12 SFX sur 40 s = 0.
10. **Fini pro** : aucun visage coupé, aucun bug visuel, image dès 0 s (pas d'écran noir), tient la comparaison avec la réf. Cam : `cam_noirs_P1` 1-8, `cam_P99` ≤ 235, `cam_neon_%` < 0,5. Cadre (info) : `yeux_y_%` ; attention, la réf FINAL.mp4 est une AUTRE rush, filmée serré (34 %) ; Meta Verified est filmée large (48 %) et son monteur ne l'a pas recadrée. Après `cadre.py`, `yeux_y_%` doit être entre 30 et 40.

**Chez un client** : `python3 $S/note.py <dossier du reel>` fait tout ça sans réf (grille seule, `oeil.json` pour ce que l'œil seul voit) + garde-fous bloquants + historique des versions (`note.json`). Process : `mode-client.md`.
**Le juge** : un sous-agent Claude séparé, qui n'a pas monté, regarde la planche d'images, le hook, le lint, le pic et le volume, et note /10 sur la grille (16:9 : `note-10-youtube.md`). Je ne refuse un retour qu'avec une preuve (mesure, image, règle de l'utilisateur).
Note < 9 → corriger seulement les défauts listés, refaire le rendu, rejuger. 3 tours max ; au-delà, livrer avec la vraie note et ce qui bloque. Méthode complète : Brain `09-SOP/boucle-9-sur-10.md`.
Ne pas se gonfler la note : en cas de doute, 0.5 (RUSH noté 9,3 par moi 3 tours de retours après).
Livrer `final.mp4` + la note /10 + une ligne par critère raté + ce qui n'a pas pu être fait (ex : un logo introuvable en vrai).
Quand l'utilisateur donne sa note : si l'écart avec la note auto est ≥ 2 points, durcir le critère concerné dans cette grille.
