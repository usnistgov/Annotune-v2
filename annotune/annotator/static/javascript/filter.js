document.addEventListener('DOMContentLoaded', function() {
    const recommendedDocId = '{{ recommended_doc_id }}';
    const accordionItems = document.querySelectorAll('.accordion-item');
    const accordionContainer = document.getElementById('keywordsAccordion');
    let recommendedAccordionItem;

    accordionItems.forEach(item => {
        const topicIdsDivs = item.querySelectorAll('.topic_ids span');
        const topicIds = Array.from(topicIdsDivs).map(span => span.textContent.trim());

        if (topicIds.includes(recommendedDocId)) {
            const button = item.querySelector('.accordion-button');
            recommendedAccordionItem = item;
            button.click();  // Automatically click the accordion button

            // Filter the table rows based on the topic IDs
            const tableRows = document.querySelectorAll('table tbody tr');
            const tbody = document.getElementById('text-table-body');
            let recommendedRow;

            tableRows.forEach(row => {
                const docId = row.querySelector('td:first-child').textContent.trim();
                if (docId === recommendedDocId) {
                    recommendedRow = row;
                    row.style.backgroundColor = '#ffffcc';  // Highlight the recommended document
                }
                if (topicIds.includes(docId)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });

            // Move the recommended document to the top of the table
            if (recommendedRow) {
                tbody.prepend(recommendedRow);
            }
        }
    });

    // Move the recommended accordion item to the top of the list
    if (recommendedAccordionItem) {
        accordionContainer.prepend(recommendedAccordionItem);
    }

    // Add event listeners for manual clicks
    const accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const accordionItem = this.closest('.accordion-item');
            const topicIdsDivs = accordionItem.querySelectorAll('.topic_ids span');
            const topicIds = Array.from(topicIdsDivs).map(span => span.textContent.trim());

            // Filter the table rows based on the topic IDs
            const tableRows = document.querySelectorAll('table tbody tr');
            const tbody = document.getElementById('text-table-body');
            let recommendedRow;

            tableRows.forEach(row => {
                const docId = row.querySelector('td:first-child').textContent.trim();
                if (docId === recommendedDocId) {
                    recommendedRow = row;
                    row.style.backgroundColor = '#ffffcc';  // Highlight the recommended document
                }
                if (topicIds.includes(docId)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });

            // Move the recommended document to the top of the ta ble
            if (recommendedRow) {
                tbody.prepend(recommendedRow);
            }
        });
    });
});