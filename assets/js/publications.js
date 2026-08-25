fetch('data/publications.json')
    .then(response => response.json())
    .then(publications => {

        const container = document.getElementById('publications');

        container.innerHTML = '';


        /*
         * ----------------------------------------
         * GROUP PUBLICATIONS BY YEAR
         * ----------------------------------------
         */

        const publicationsByYear = {};

        publications.forEach(publication => {

            const year = publication.year || 'Unknown year';

            if (!publicationsByYear[year]) {
                publicationsByYear[year] = [];
            }

            publicationsByYear[year].push(publication);

        });


        /*
         * ----------------------------------------
         * SORT YEARS
         * Newest first
         * ----------------------------------------
         */

        const years = Object.keys(publicationsByYear).sort(
            (a, b) => b.localeCompare(a)
        );


        /*
         * ----------------------------------------
         * CREATE EACH YEAR SECTION
         * ----------------------------------------
         */

        years.forEach((year, index) => {

            const yearSection = document.createElement('div');

            yearSection.className = 'publication-year';


            /*
             * Year heading
             */

            const yearButton = document.createElement('button');

            yearButton.className = 'publication-year-button';

            yearButton.innerHTML = `
                <span class="year-arrow">
                    ${index === 0 ? '▼' : '▶'}
                </span>
                ${year}
            `;


            /*
             * Publications container
             */

            const yearPublications = document.createElement('div');

            yearPublications.className =
                'publication-year-content';


            /*
             * First year is open.
             * All other years are collapsed.
             */

            if (index !== 0) {
                yearPublications.style.display = 'none';
            }


            /*
             * ----------------------------------------
             * ADD PUBLICATIONS TO YEAR
             * ----------------------------------------
             */

            publicationsByYear[year].forEach(publication => {

                const article =
                    document.createElement('article');


                /*
                 * AUTHORS
                 */

                let authorsHTML = '';

                if (
                    publication.authors &&
                    publication.authors.length > 0
                ) {

                    authorsHTML =
                        publication.authors.map(author => {

                            /*
                             * Normalise name for comparison
                             */

                            const normalisedAuthor =
                                author
                                    .normalize("NFD")
                                    .replace(
                                        /[\u0300-\u036f]/g,
                                        ""
                                    )
                                    .toLowerCase()
                                    .replace(
                                        /[.,]/g,
                                        ""
                                    )
                                    .replace(
                                        /\s+/g,
                                        " "
                                    )
                                    .trim();


                            /*
                             * Recognise your different
                             * name variations
                             */

                            const isAlejandro = (

                                normalisedAuthor.includes(
                                    "alejandro gonzalez-aquines"
                                )

                                ||

                                normalisedAuthor.includes(
                                    "alejandro gonzalez aquines"
                                )

                                ||

                                normalisedAuthor.includes(
                                    "gonzalez-aquines a"
                                )

                                ||

                                normalisedAuthor.includes(
                                    "gonzalez aquines a"
                                )

                            );


                            if (isAlejandro) {

                                return `
                                    <strong>
                                        ${author}
                                    </strong>
                                `;

                            }

                            return author;

                        }).join(', ');

                }


                /*
                 * DOI
                 */

                let doiHTML = '';

                if (publication.doi) {

                    const doiURL =
                        publication.doi.startsWith('http')
                            ? publication.doi
                            : `https://doi.org/${publication.doi}`;


                    doiHTML = `
                        <br>
                        DOI:
                        <a
                            href="${doiURL}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            ${doiURL}
                        </a>
                    `;

                }


                /*
                 * PUBLICATION
                 */

                article.innerHTML = `

                    <h4 class="publication-title">
                        ${publication.title}
                    </h4>

                    <p class="publication-details">

                        ${authorsHTML}<br>

                        <em>
                            ${publication.journal}
                        </em>,
                        ${publication.year}

                        ${doiHTML}

                    </p>

                `;


                yearPublications.appendChild(article);

            });


            /*
             * ----------------------------------------
             * CLICK YEAR TO OPEN/CLOSE
             * ----------------------------------------
             */

            yearButton.addEventListener(
                'click',
                function () {

                    const isOpen =
                        yearPublications.style.display !== 'none';


                    if (isOpen) {

                        yearPublications.style.display =
                            'none';

                        yearButton.querySelector(
                            '.year-arrow'
                        ).textContent = '▶';

                    } else {

                        yearPublications.style.display =
                            'block';

                        yearButton.querySelector(
                            '.year-arrow'
                        ).textContent = '▼';

                    }

                }
            );


            /*
             * Add everything to the page
             */

            yearSection.appendChild(yearButton);

            yearSection.appendChild(
                yearPublications
            );

            container.appendChild(
                yearSection
            );

        });

    })


    /*
     * ----------------------------------------
     * ERROR HANDLING
     * ----------------------------------------
     */

    .catch(error => {

        console.error(
            'Error loading publications:',
            error
        );

        document.getElementById(
            'publications'
        ).innerHTML =
            '<p>Publications could not be loaded.</p>';

    });