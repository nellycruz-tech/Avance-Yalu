import sys
from PIL import Image
from io import BytesIO
from huey.contrib.djhuey import task
from django.core.files.uploadedfile import InMemoryUploadedFile

@task()
def optimizar_imagen_async(imagen_id):
    from catalogo.models import ImagenProducto
    try:
        instance = ImagenProducto.objects.get(id=imagen_id)
        # Verificamos si aún necesita optimización (por si ya se procesó)
        if instance.imagen and not instance.imagen.name.lower().endswith('.webp'):
            archivo_optimizado = optimizar_imagen(instance.imagen)
            instance.imagen.save(archivo_optimizado.name, archivo_optimizado, save=False)
            instance.save(update_fields=['imagen'])
    except Exception as e:
        print(f"Error en tarea de fondo: {e}")

def optimizar_imagen(imagen_field, max_width=1000):
    img = Image.open(imagen_field)
    
    if img.format == 'GIF':
        buffer = BytesIO()
        img.save(buffer, format="WEBP", save_all=True, quality=60, method=6)
        buffer.seek(0)
        nombre_base = imagen_field.name.rsplit('.', 1)[0]
        return InMemoryUploadedFile(
            buffer, 'ImageField', f"{nombre_base}.webp", 'image/webp', sys.getsizeof(buffer), None
        )

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=75, optimize=True)
    buffer.seek(0)
    
    nombre_base = imagen_field.name.rsplit('.', 1)[0]
    return InMemoryUploadedFile(
        buffer, 'ImageField', f"{nombre_base}.webp", 'image/webp', sys.getsizeof(buffer), None
    )