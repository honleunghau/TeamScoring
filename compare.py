# compare.py
# CLI to compare two images, extract scores, show difference and IMPs.

import sys
from ocr_utils import extract_scores_from_image, choose_most_likely_score
from imp import points_to_imps

def compare_images(img1: str, img2: str):
    cand1 = extract_scores_from_image(img1)
    cand2 = extract_scores_from_image(img2)

    score1 = choose_most_likely_score(cand1)
    score2 = choose_most_likely_score(cand2)

    if score1 is None:
        print(f"No numeric score found in {img1}. Candidates: {cand1}")
        return
    if score2 is None:
        print(f"No numeric score found in {img2}. Candidates: {cand2}")
        return

    diff = score1 - score2
    imps = points_to_imps(abs(diff))

    print("Image 1:", img1)
    print("  Candidates:", cand1)
    print("  Chosen score:", score1)
    print()
    print("Image 2:", img2)
    print("  Candidates:", cand2)
    print("  Chosen score:", score2)
    print()
    print("Point difference (img1 - img2):", diff)
    print("IMP result:", imps)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare.py <image1> <image2>")
        sys.exit(1)
    compare_images(sys.argv[1], sys.argv[2])
