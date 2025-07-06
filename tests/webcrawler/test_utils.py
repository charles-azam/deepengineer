from deepengineer.webcrawler.utils import sanitize_filename


def test_sanitize_filename():
    assert sanitize_filename("My Document!@#$%^&*.txt") == "My_Document_.txt"
    assert (
        sanitize_filename("  Another file with spaces & special_chars  ")
        == "Another_file_with_spaces_special_chars"
    )
    assert (
        sanitize_filename("Düsseldorf_Report_2023.pdf") == "Dusseldorf_Report_2023.pdf"
    )
    assert (
        sanitize_filename("File with an é, ö, ü, ç, ñ.docx")
        == "File_with_an_e_o_u_c_n.docx"
    )
    assert sanitize_filename("Очень важное дело.xlsx") == "_xlsx"
    assert (
        sanitize_filename(
            "My.Super.Duper.File.Name.with.lots.of.dots.and.A@#!!%@#$%^&*.txt"
        )
        == "My.Super.Duper.File.Name.with.lots.of.dots.and.A_.txt"
    )
    assert sanitize_filename("........hidden_file.txt") == "_.......hidden_file.txt"
    assert (
        sanitize_filename(
            "A very long file name that exceeds typical operating system limits and needs to be truncated gracefully.zip"
        )
        == "A_very_long_file_name_that_exceeds_typical_operating_system_limits_and_needs_to_be_truncated_gracefully.zip"
    )
    assert sanitize_filename(" ") == "untitled_file"
    assert sanitize_filename("!") == "untitled_file"
    assert sanitize_filename("  .some_hidden_file.txt  ") == "_some_hidden_file.txt"
    assert (
        sanitize_filename("file_name_with_________many_underscores.txt")
        == "file_name_with_many_underscores.txt"
    )
