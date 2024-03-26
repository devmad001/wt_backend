import fitz

### READ IN PDF
doc = fitz.open("page1sample.pdf")

for page in doc:
    ### SEARCH
    # text = "124,361"
    texts = ['553']
    for text in texts:
        text_instances = page.search_for(str(text))

        ### HIGHLIGHT
        for inst in text_instances:
            row_rect = fitz.Rect(0, inst.y0, page.rect.width, inst.y1)
            highlight = page.add_highlight_annot(row_rect)
            highlight.update()


### OUTPUT
doc.save("output_aug11.pdf", garbage=4, deflate=True, clean=True)
