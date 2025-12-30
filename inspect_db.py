from app import app, db, Translation

with app.app_context():
    # Get the last translation
    last_translation = Translation.query.order_by(Translation.id.desc()).first()
    if last_translation:
        print(f"ID: {last_translation.id}")
        print(f"Original: {last_translation.original_text}")
        print(f"Translated: {last_translation.translated_text}")
        print(f"Is Special Report: {last_translation.is_special_report}")
    else:
        print("No translations found.")
