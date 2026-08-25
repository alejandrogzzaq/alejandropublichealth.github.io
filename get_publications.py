import requests
import json
import time

ORCID_ID = "0000-0002-9377-6494"

ORCID_HEADERS = {
    "Accept": "application/vnd.orcid+json"
}

CROSSREF_HEADERS = {
    "User-Agent": "Alejandro Gonzalez-Aquines academic website"
}


# ============================================================
# CROSSREF: GET AUTHORS FROM DOI
# ============================================================

def get_crossref_authors(doi):

    if not doi:
        return []

    # Remove DOI URL if necessary
    doi = doi.replace(
        "https://doi.org/",
        ""
    ).replace(
        "http://doi.org/",
        ""
    ).strip()

    url = f"https://api.crossref.org/works/{doi}"

    try:

        response = requests.get(
            url,
            headers=CROSSREF_HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        work = data.get(
            "message",
            {}
        )

        crossref_authors = []

        for author in work.get(
            "author",
            []
        ):

            given = author.get(
                "given",
                ""
            ).strip()

            family = author.get(
                "family",
                ""
            ).strip()

            if given and family:

                crossref_authors.append(
                    f"{given} {family}"
                )

            elif family:

                crossref_authors.append(
                    family
                )

        return crossref_authors

    except Exception as error:

        print(
            f"Crossref error for DOI {doi}: "
            f"{error}"
        )

        return []


# ============================================================
# ORCID: GET PUBLICATIONS
# ============================================================

url = (
    f"https://pub.orcid.org/v3.0/"
    f"{ORCID_ID}/works"
)

response = requests.get(
    url,
    headers=ORCID_HEADERS
)

print(
    "ORCID status code:",
    response.status_code
)

if response.status_code != 200:

    print(
        "Could not retrieve publications "
        "from ORCID."
    )

    print(response.text)

    exit()


data = response.json()

publications = []


# ============================================================
# PROCESS EACH PUBLICATION
# ============================================================

for group in data.get(
    "group",
    []
):

    summaries = group.get(
        "work-summary",
        []
    )

    if not summaries:
        continue


    summary = summaries[0]


    put_code = summary.get(
        "put-code"
    )

    if not put_code:
        continue


    # --------------------------------------------------------
    # Retrieve complete ORCID work
    # --------------------------------------------------------

    work_url = (
        f"https://pub.orcid.org/v3.0/"
        f"{ORCID_ID}/work/{put_code}"
    )

    work_response = requests.get(
        work_url,
        headers=ORCID_HEADERS
    )

    if work_response.status_code != 200:

        print(
            f"Could not retrieve work "
            f"{put_code}"
        )

        continue


    work = work_response.json()


    # ========================================================
    # TITLE
    # ========================================================

    title = (
        work.get(
            "title",
            {}
        )
        .get(
            "title",
            {}
        )
        .get(
            "value",
            ""
        )
    )


    # ========================================================
    # JOURNAL
    # ========================================================

    journal = ""

    journal_data = work.get(
        "journal-title"
    )

    if journal_data:

        journal = journal_data.get(
            "value",
            ""
        )


    # ========================================================
    # PUBLICATION YEAR
    # ========================================================

    year = ""

    publication_date = work.get(
        "publication-date"
    )

    if publication_date:

        year_data = publication_date.get(
            "year"
        )

        if year_data:

            year = year_data.get(
                "value",
                ""
            )


    # ========================================================
    # DOI
    # ========================================================

    doi = ""

    external_ids_data = (
        work.get(
            "external-ids"
        ) or {}
    )

    external_ids = (
        external_ids_data.get(
            "external-id"
        ) or []
    )


    for external_id in external_ids:

        if not external_id:
            continue


        doi_type = (
            external_id.get(
                "external-id-type"
            ) or ""
        ).lower()


        if doi_type == "doi":

            doi = (
                external_id.get(
                    "external-id-value"
                ) or ""
            )

            break


    # ========================================================
    # AUTHORS FROM ORCID
    # ========================================================

    authors = []

    contributors = (
        work.get(
            "contributors"
        ) or {}
    )

    contributor_list = (
        contributors.get(
            "contributor"
        ) or []
    )


    for contributor in contributor_list:

        credit_name = contributor.get(
            "credit-name"
        )

        if credit_name:

            author_name = (
                credit_name.get(
                    "value",
                    ""
                )
            )

            if author_name:

                authors.append(
                    author_name
                )


    # ========================================================
    # CROSSREF FALLBACK
    # ========================================================

    if not authors and doi:

        print(
            f"No authors in ORCID for:"
        )

        print(title)

        print(
            "Trying Crossref..."
        )


        crossref_authors = (
            get_crossref_authors(doi)
        )


        if crossref_authors:

            authors = crossref_authors

            print(
                f"Crossref found "
                f"{len(authors)} authors."
            )

        else:

            print(
                "Crossref could not find "
                "the authors."
            )


    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    print()
    print(
        "Publication:",
        title
    )

    print(
        "Authors:",
        authors
    )

    print(
        "Journal:",
        journal
    )

    print(
        "Year:",
        year
    )

    print(
        "DOI:",
        doi
    )


    # ========================================================
    # SAVE PUBLICATION
    # ========================================================

    publications.append({

        "title": title,

        "authors": authors,

        "journal": journal,

        "year": year,

        "doi": doi

    })


    # Small delay between requests

    time.sleep(0.2)


# ============================================================
# SORT PUBLICATIONS
# ============================================================

publications.sort(
    key=lambda x: x["year"],
    reverse=True
)


# ============================================================
# SAVE JSON
# ============================================================

with open(
    "data/publications.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        publications,
        file,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# FINISHED
# ============================================================

print()

print(
    f"Successfully retrieved "
    f"{len(publications)} publications."
)

print(
    "Saved to data/publications.json"
)