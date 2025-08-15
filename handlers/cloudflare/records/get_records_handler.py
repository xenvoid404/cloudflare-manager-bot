elif callback_data == "get_records":
            await query.edit_message_text(
                text="🚧 *Fitur Lihat Record DNS*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n"
                "Akan menampilkan semua record DNS yang ada di zone Anda\\.\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )