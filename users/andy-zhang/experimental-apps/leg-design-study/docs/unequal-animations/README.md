# Upper-long inversion illustrations within 1.25x

Four current offline GIFs show upper25/50/75/100:200/170,200/175,205/185 and
215/175 mm. All have longer/shorter<=1.25, alpha=phase=0. Blue is upper,
orange is lower; wheel radius200 mm and guide pitch circles are true scale.
Each 80-frame six-second cycle sweeps q100-260 and back, including exact fold180.

The wheel and upper rod overlap in side projection at the fold. Captions explicitly
require axial wheel/link separation. These are equation-based illustrations,
not collision/contact or hardware validation. Wheel orientation is held;
no no-slip rolling constraint is imposed. Earlier broad clearNN examples are
superseded and remain in Git revision aaed324, not the current folder.

Rebuild with `python scripts/build_unequal_visuals.py` using the pinned local
Pillow environment. Manifest records hashes, parameters, frame size and duration.
Keep this folder beside the offline HTML. Raw QA frames stay ignored.
