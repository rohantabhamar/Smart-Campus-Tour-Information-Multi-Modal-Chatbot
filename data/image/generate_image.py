"""
data/download_images.py
-----------------------
Downloads 10 free campus-relevant images per category from Unsplash CDN.
No API key needed.

Categories (13 total):
  library, cafeteria, lecture_hall, gym, it_lab, lab,
  admin_office, outdoor, auditorium, student_union,
  career_center, medical_center, engineering
"""

import os
import urllib.request
import time
from PIL import Image as PILImage

# ---------------------------------------------------------------------------
# Category → KB location mapping
# ---------------------------------------------------------------------------
CATEGORY_TO_KB = {
    "library":       "Main Library",
    "cafeteria":     "Main Cafeteria",
    "lecture_hall":  "Main Auditorium",
    "gym":           "Sports & Fitness Centre",
    "it_lab":        "IT & Computer Lab",
    "lab":           "IT & Computer Lab",
    "admin_office":  "Admissions & Registry Office",
    "outdoor":       "Campus Garden & Outdoor Study Area",
    "auditorium":    "Main Auditorium",
    "student_union": "Student Union",
    "career_center": "Career Services Centre",
    "medical_center":"Medical & Counselling Centre",
    "engineering":   "Engineering College - Main Block",
}

categories = list(CATEGORY_TO_KB.keys())

for cat in categories:
    os.makedirs(f"data/images/{cat}", exist_ok=True)

# ---------------------------------------------------------------------------
# Image URLs — 10 per category
# ---------------------------------------------------------------------------
images = {
    "library": [
        ("https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=640&q=80", "library_01.jpg"),
        ("https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=640&q=80", "library_02.jpg"),
        ("https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=640&q=80", "library_03.jpg"),
        ("https://images.unsplash.com/photo-1568667256549-094345857637?w=640&q=80", "library_04.jpg"),
        ("https://images.unsplash.com/photo-1572883454114-1cf0031ede2a?w=640&q=80", "library_05.jpg"),
        ("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=640&q=80", "library_06.jpg"),
        ("https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=640&q=80", "library_07.jpg"),
        ("https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=640&q=80", "library_08.jpg"),
        ("https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=640&q=80", "library_09.jpg"),
        ("https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=640&q=80", "library_10.jpg"),
    ],
    "cafeteria": [
        ("https://images.unsplash.com/photo-1567521464027-f127ff144326?w=640&q=80", "cafeteria_01.jpg"),
        ("https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=640&q=80", "cafeteria_02.jpg"),
        ("https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=640&q=80", "cafeteria_03.jpg"),
        ("https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=640&q=80", "cafeteria_04.jpg"),
        ("https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=640&q=80", "cafeteria_05.jpg"),
        ("https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?w=640&q=80", "cafeteria_06.jpg"),
        ("https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=640&q=80", "cafeteria_07.jpg"),
        ("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=640&q=80", "cafeteria_08.jpg"),
        ("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=640&q=80", "cafeteria_09.jpg"),
        ("https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=640&q=80", "cafeteria_10.jpg"),
    ],
    "lecture_hall": [
        ("https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=640&q=80", "lecture_01.jpg"),
        ("https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?w=640&q=80", "lecture_02.jpg"),
        ("https://images.unsplash.com/photo-1509062522246-3755977927d7?w=640&q=80", "lecture_03.jpg"),
        ("https://images.unsplash.com/photo-1558008258-3256797b43f3?w=640&q=80", "lecture_04.jpg"),
        ("https://images.unsplash.com/photo-1571260899304-425eee4c7efc?w=640&q=80", "lecture_05.jpg"),
        ("https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=640&q=80", "lecture_06.jpg"),
        ("https://images.unsplash.com/photo-1576267423445-b2e0074d68a4?w=640&q=80", "lecture_07.jpg"),
        ("https://images.unsplash.com/photo-1564981797816-1043664bf78d?w=640&q=80", "lecture_08.jpg"),
        ("https://images.unsplash.com/photo-1594608661623-aa0bd3a69799?w=640&q=80", "lecture_09.jpg"),
        ("https://images.unsplash.com/photo-1610484826967-09c5720778c7?w=640&q=80", "lecture_10.jpg"),
    ],
    "gym": [
        ("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=640&q=80", "gym_01.jpg"),
        ("https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=640&q=80", "gym_02.jpg"),
        ("https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=640&q=80", "gym_03.jpg"),
        ("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=640&q=80", "gym_04.jpg"),
        ("https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?w=640&q=80", "gym_05.jpg"),
        ("https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=640&q=80", "gym_06.jpg"),
        ("https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=640&q=80", "gym_07.jpg"),
        ("https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=640&q=80", "gym_08.jpg"),
        ("https://images.unsplash.com/photo-1549060279-7e168fcee0c2?w=640&q=80", "gym_09.jpg"),
        ("https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=640&q=80", "gym_10.jpg"),
    ],
    "it_lab": [
        ("https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=640&q=80", "itlab_01.jpg"),
        ("https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=640&q=80", "itlab_02.jpg"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=640&q=80", "itlab_03.jpg"),
        ("https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=640&q=80", "itlab_04.jpg"),
        ("https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=640&q=80", "itlab_05.jpg"),
        ("https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=640&q=80", "itlab_06.jpg"),
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=640&q=80", "itlab_07.jpg"),
        ("https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=640&q=80", "itlab_08.jpg"),
        ("https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=640&q=80", "itlab_09.jpg"),
        ("https://images.unsplash.com/photo-1555099962-4199c345e5dd?w=640&q=80", "itlab_10.jpg"),
    ],
    "lab": [
        ("https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=640&q=80", "lab_01.jpg"),
        ("https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=640&q=80", "lab_02.jpg"),
        ("https://images.unsplash.com/photo-1576086213369-97a306d36557?w=640&q=80", "lab_03.jpg"),
        ("https://images.unsplash.com/photo-1614935151651-0bea6508db6b?w=640&q=80", "lab_04.jpg"),
        ("https://images.unsplash.com/photo-1559757175-5700dde675bc?w=640&q=80", "lab_05.jpg"),
        ("https://images.unsplash.com/photo-1581093450021-4a7360e9a6b5?w=640&q=80", "lab_06.jpg"),
        ("https://images.unsplash.com/photo-1563213126-a4273aed2016?w=640&q=80", "lab_07.jpg"),
        ("https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=640&q=80", "lab_08.jpg"),
        ("https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=640&q=80", "lab_09.jpg"),
        ("https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?w=640&q=80", "lab_10.jpg"),
    ],
    "admin_office": [
        ("https://images.unsplash.com/photo-1497366216548-37526070297c?w=640&q=80", "office_01.jpg"),
        ("https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=640&q=80", "office_02.jpg"),
        ("https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=640&q=80", "office_03.jpg"),
        ("https://images.unsplash.com/photo-1556761175-4b46a572b786?w=640&q=80", "office_04.jpg"),
        ("https://images.unsplash.com/photo-1505409859467-3a796fd5798e?w=640&q=80", "office_05.jpg"),
        ("https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=640&q=80", "office_06.jpg"),
        ("https://images.unsplash.com/photo-1572025442646-866d16c84a54?w=640&q=80", "office_07.jpg"),
        ("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=640&q=80", "office_08.jpg"),
        ("https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=640&q=80", "office_09.jpg"),
        ("https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=640&q=80", "office_10.jpg"),
    ],
    "outdoor": [
        ("https://images.unsplash.com/photo-1562774053-701939374585?w=640&q=80", "outdoor_01.jpg"),
        ("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=640&q=80", "outdoor_02.jpg"),
        ("https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=640&q=80", "outdoor_03.jpg"),
        ("https://images.unsplash.com/photo-1607237138185-eedd9c632b0b?w=640&q=80", "outdoor_04.jpg"),
        ("https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?w=640&q=80", "outdoor_05.jpg"),
        ("https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=640&q=80", "outdoor_06.jpg"),
        ("https://images.unsplash.com/photo-1590650213165-c1fef80648c4?w=640&q=80", "outdoor_07.jpg"),
        ("https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=640&q=80", "outdoor_08.jpg"),
        ("https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=640&q=80", "outdoor_09.jpg"),
        ("https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=640&q=80", "outdoor_10.jpg"),
    ],
    "auditorium": [
        ("https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=640&q=80", "auditorium_01.jpg"),
        ("https://images.unsplash.com/photo-1531058020387-3be344556be6?w=640&q=80", "auditorium_02.jpg"),
        ("https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=640&q=80", "auditorium_03.jpg"),
        ("https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=640&q=80", "auditorium_04.jpg"),
        ("https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=640&q=80", "auditorium_05.jpg"),
        ("https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=640&q=80", "auditorium_06.jpg"),
        ("https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=640&q=80", "auditorium_07.jpg"),
        ("https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=640&q=80", "auditorium_08.jpg"),
        ("https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=640&q=80", "auditorium_09.jpg"),
        ("https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=640&q=80", "auditorium_10.jpg"),
    ],
    "student_union": [
        ("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=640&q=80", "union_01.jpg"),
        ("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=640&q=80", "union_02.jpg"),
        ("https://images.unsplash.com/photo-1543269865-cbf427effbad?w=640&q=80", "union_03.jpg"),
        ("https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=640&q=80", "union_04.jpg"),
        ("https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=640&q=80", "union_05.jpg"),
        ("https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=640&q=80", "union_06.jpg"),
        ("https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=640&q=80", "union_07.jpg"),
        ("https://images.unsplash.com/photo-1573164713988-8665fc963095?w=640&q=80", "union_08.jpg"),
        ("https://images.unsplash.com/photo-1550439062-609e1531270e?w=640&q=80", "union_09.jpg"),
        ("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=640&q=80", "union_10.jpg"),
    ],
    "career_center": [
        ("https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=640&q=80", "career_01.jpg"),
        ("https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=640&q=80", "career_02.jpg"),
        ("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=640&q=80", "career_03.jpg"),
        ("https://images.unsplash.com/photo-1560472355-536de3962603?w=640&q=80", "career_04.jpg"),
        ("https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=640&q=80", "career_05.jpg"),
        ("https://images.unsplash.com/photo-1551434678-e076c223a692?w=640&q=80", "career_06.jpg"),
        ("https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=640&q=80", "career_07.jpg"),
        ("https://images.unsplash.com/photo-1553877522-43269d4ea984?w=640&q=80", "career_08.jpg"),
        ("https://images.unsplash.com/photo-1556761175-5994b5a5a59b?w=640&q=80", "career_09.jpg"),
        ("https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=640&q=80", "career_10.jpg"),
    ],
    "medical_center": [
        ("https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=640&q=80", "medical_01.jpg"),
        ("https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=640&q=80", "medical_02.jpg"),
        ("https://images.unsplash.com/photo-1516549655169-df83a0774514?w=640&q=80", "medical_03.jpg"),
        ("https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=640&q=80", "medical_04.jpg"),
        ("https://images.unsplash.com/photo-1551601651-2a8555f1a136?w=640&q=80", "medical_05.jpg"),
        ("https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=640&q=80", "medical_06.jpg"),
        ("https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=640&q=80", "medical_07.jpg"),
        ("https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=640&q=80", "medical_08.jpg"),
        ("https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=640&q=80", "medical_09.jpg"),
        ("https://images.unsplash.com/photo-1504813184591-01572f98c85f?w=640&q=80", "medical_10.jpg"),
    ],
    "engineering": [
        ("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=640&q=80", "engineering_01.jpg"),
        ("https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?w=640&q=80", "engineering_02.jpg"),
        ("https://images.unsplash.com/photo-1518770660439-4636190af475?w=640&q=80", "engineering_03.jpg"),
        ("https://images.unsplash.com/photo-1562408590-e32931084e23?w=640&q=80", "engineering_04.jpg"),
        ("https://images.unsplash.com/photo-1533749871411-5e21e14bcc7d?w=640&q=80", "engineering_05.jpg"),
        ("https://images.unsplash.com/photo-1566228015668-4c45dbc4e2f5?w=640&q=80", "engineering_06.jpg"),
        ("https://images.unsplash.com/photo-1565814636199-ae8133055c1c?w=640&q=80", "engineering_07.jpg"),
        ("https://images.unsplash.com/photo-1580584126903-c17d41830450?w=640&q=80", "engineering_08.jpg"),
        ("https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=640&q=80", "engineering_09.jpg"),
        ("https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?w=640&q=80", "engineering_10.jpg"),
    ],
}

# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

total_success = 0
total_failed  = 0
failed_list   = []

print("=" * 55)
print("   DOWNLOADING CAMPUS IMAGES")
print(f"   {len(categories)} categories x 10 images = {len(categories)*10} total")
print("=" * 55)

for category, img_list in images.items():
    print(f"\n{category.upper()} ({len(img_list)} images)")
    print("  " + "-" * 40)

    for url, fname in img_list:
        path = f"data/images/{category}/{fname}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                with open(path, "wb") as f:
                    f.write(response.read())

            size = os.path.getsize(path) / 1024
            if size < 5:
                os.remove(path)
                raise Exception(f"File too small ({size:.1f} KB)")

            print(f"  OK  {fname} ({size:.0f} KB)")
            total_success += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"  FAIL {fname} — {e}")
            total_failed += 1
            failed_list.append(f"{category}/{fname}")
            time.sleep(0.3)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 55)
print("   DOWNLOAD SUMMARY")
print("=" * 55)
print(f"  Successfully downloaded : {total_success}")
print(f"  Failed                  : {total_failed}")

print(f"\nImages per category:")
total_images = 0
for cat in categories:
    folder = f"data/images/{cat}"
    files  = [f for f in os.listdir(folder)
               if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    count  = len(files)
    total_images += count
    bar    = "#" * count + "-" * (10 - count)
    kb_loc = CATEGORY_TO_KB.get(cat, cat)
    print(f"  {cat:<20} [{bar}] {count}/10  → {kb_loc}")

print(f"\n  Total images : {total_images}")

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
print(f"\nValidating images...")
valid = invalid = 0

for cat in categories:
    folder = f"data/images/{cat}"
    for fname in os.listdir(folder):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            fpath = os.path.join(folder, fname)
            try:
                img = PILImage.open(fpath)
                img.verify()
                valid += 1
            except Exception:
                print(f"  Invalid: {cat}/{fname} — removing")
                os.remove(fpath)
                invalid += 1

print(f"  Valid images   : {valid}")
print(f"  Invalid removed: {invalid}")
print("\nDONE. Images ready in data/images/")
