from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import numpy as np
import os
from backend.business.models import Business, BusinessAddress, BusinessKeywordSuggestions, BusinessReview
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


COLOR_AMARILLO = "#FFE9A0"
COLOR_NARANJA = "#FE4F2D"
COLOR_AZUL = "#57B4BA"
COLOR_OSCURO = "#015551"
COLOR_BLANCO = "#FFFFFF"

basedir = os.path.dirname(os.path.abspath(__file__))

# Navegamos 'hacia arriba' desde backend/ y luego 'hacia abajo' a frontend/
images_dir = os.path.join(basedir, '..','..', 'frontend', 'resources')

# Variables
def generate_completeness_graphic(grado_completitud):
    # Colores
    color_fondo = "#FFE9A0"
    color_ok = "#57B4BA"
    color_valor = "#FE4F2D"

    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw={'projection': 'polar'})
    ax.set_facecolor(color_fondo)

    # Semicírculo
    angles = np.linspace(np.pi, 0, 100)
    ax.plot(angles, [1]*100, color=color_ok, lw=20, alpha=0.3)  # fondo
    angle_value = np.pi * (1 - grado_completitud / 100)
    ax.plot(np.linspace(np.pi, angle_value, 100), [1]*100, color=color_valor, lw=20)

    # Texto
    ax.text(0, 0, f"{grado_completitud:.1f}", ha='center', va='center', fontsize=24, color="#015551")
    ax.text(0, -0.3, "Grado de completitud del perfil", ha='center', va='center', fontsize=10, color="#015551")

    # Formato visual
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_ylim(0, 1.1)
    ax.spines['polar'].set_visible(False)
    ax.grid(False)

    # Guardar imagen
    gauge_path = "gauge_completitud.png"
    plt.savefig(gauge_path, bbox_inches='tight', facecolor=color_fondo)
    plt.close()

    return gauge_path

def dibujar_fondo_y_encabezado(canvas, doc, business_data, logo_path):
    width, height = letter

    # Fondo amarillo
    canvas.setFillColor(colors.HexColor(COLOR_AMARILLO))
    canvas.rect(0, 0, width, height, fill=1)

    # Cabecera blanca
    cabecera_altura = 1.2 * inch
    canvas.setFillColor(colors.HexColor(COLOR_BLANCO))
    canvas.rect(0, height - cabecera_altura, width, cabecera_altura, fill=1)

    # Logo
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, width - 1.4*inch, height - 1*inch, width=1*inch, height=1*inch, mask='auto')

    # Título
    canvas.setFont("Helvetica-Bold", 26)
    canvas.setFillColor(colors.HexColor(COLOR_NARANJA))
    canvas.drawString(inch, height - 0.7*inch, f"Informe de SEO Local: {business_data.nombre}")

    # Dirección
    if business_data.direccion and business_data.direccion.direccion_completa:
        canvas.setFont("Helvetica", 14)
        canvas.drawString(inch, height - 0.95*inch, business_data.direccion.direccion_completa)



def generate_seo_report_pdf(business_data: Business, output_filename="informe_seo_dinamico.pdf"):
    styles = getSampleStyleSheet()
    doc = BaseDocTemplate(output_filename, pagesize=letter)

    frame = Frame(
        0.5* inch, inch * 0.5,
        doc.width, doc.height,
        leftPadding=8, rightPadding=8, topPadding=6, bottomPadding=8
    )
    

    def on_page(canvas, doc):
        dibujar_fondo_y_encabezado(canvas, doc, business_data, images_dir+'logo1-SEOlocalizer-sinfondo.png')

    template = PageTemplate(id="plantillaSEO", frames=frame, onPage=on_page)
    doc.addPageTemplates([template])

    story = []

    # Estilos
    h1_style = ParagraphStyle(
        'h2_custom',
        parent=styles['Heading2'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor(COLOR_NARANJA),
        backColor=colors.HexColor(COLOR_AMARILLO),
        spaceAfter=12,
        leftIndent=6
    )
    h2_style = ParagraphStyle(
        'h2_custom',
        parent=styles['Heading2'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor(COLOR_NARANJA),
        backColor=colors.HexColor(COLOR_AMARILLO),
        spaceAfter=12,
        leftIndent=6
    )
    h3_style = ParagraphStyle(
        'h3_custom',
        parent=styles['h3'],
        fontSize=14,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor('#333333') # Gris oscuro
    )
    normal_style = ParagraphStyle(
        'normal_custom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor(COLOR_OSCURO)
    )
    bullet_style = styles['Bullet']
    # Encabezado del informe
    # --- Layout tipo grid: [ gauge | tabla izq | tabla der ]
    
    #title=Paragraph(f"Informe de SEO Local: {business_data.nombre}", h2_style)
    #if business_data.direccion and business_data.direccion.direccion_completa:
    #    address=Paragraph(business_data.direccion.direccion_completa, h2_style)
    #logo= Image(images_dir+'logo1-SEOlocalizer-sinfondo.png', width=1*inch, height=1*inch)
    #grid_layout = Table(
    #    [[title, logo]],
    #    colWidths=[5.2*inch, 2.6*inch]
    #)
    #story.append(grid_layout)
    #story.append(Spacer(1, 0.2 * inch))
    #story.append(address)


    # --- Título de sección
    story.append(Paragraph("OPTIMIZACIÓN", h2_style))
    story.append(Spacer(1, 0.1 * inch))

    # --- Imagen del gauge
    gauge_img = Image(generate_completeness_graphic(business_data.perfil_completitud), width=1.9*inch, height= 1.5* inch)

    # --- Listas de atributos del perfil
    campos_izq = [
        ["Tiene nombre", "✅" if business_data.tiene_nombre else "❌"],
        ["Tiene dirección", "✅" if business_data.tiene_direccion else "❌"],
        ["Tiene teléfonos", "✅" if business_data.tiene_telefono else "❌"],
        ["Tiene página web asociada", "✅" if business_data.tiene_website else "❌"],
        ["Tiene categoría principal", "✅" if business_data.tiene_categoria_principal else "❌"],
        ["Tiene categorías secundarias", "✅" if business_data.tiene_categorias_secundarias else "❌"]
    ]

    campos_der = [
        ["Tiene horario", "✅" if business_data.horario_normal else "❌"],
        ["Tiene horarios especiales", "✅" if business_data.horario_festivo else "❌"],
        ["Tiene valoraciones", "✅" if business_data.tiene_valoraciones else "❌"],
        ["Tiene reseñas", "✅" if business_data.n_valoraciones and business_data.n_valoraciones > 0 else "❌"],
        ["Tiene fotos y vídeos", "✅" if business_data.tiene_fotos else "❌"],
        ["El negocio está operativo", "✅" if business_data.tiene_estado_operativo else "❌"]
    ]

    def build_card_table(data):
        table = Table(data, colWidths=[2.1*inch, 0.4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_AZUL)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor(COLOR_OSCURO)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.HexColor(COLOR_OSCURO)),
        ]))
        return table

    tabla_izquierda = build_card_table(campos_izq)
    tabla_derecha = build_card_table(campos_der)

    # --- Layout tipo grid: [ gauge | tabla izq | tabla der ]
    grid_layout = Table(
        [[gauge_img, tabla_izquierda, tabla_derecha]],
        colWidths=[2.6*inch, 2.6*inch, 2.6*inch]
    )
    grid_layout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_AMARILLO)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(grid_layout)
    story.append(Spacer(1, 0.2 * inch))

    # --- Texto explicativo
    story.append(Paragraph(
        "Recuerda que también es importante mantener la información de contacto (como dirección, teléfono, página web) y tus fotos actualizadas. Además, asegura que el enlace al sitio web funciona correctamente.",
        normal_style
    ))

    # --- Generar el PDF
    #doc.build(story)

    #return output_filename

    """doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Estilos personalizados para el informe
    h1_style = ParagraphStyle(
        'h1_custom',
        parent=styles['h1'],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'h2_custom',
        parent=styles['h2'],
        fontSize=18,
        leading=22,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#0000FF') # Azul
    )
    h3_style = ParagraphStyle(
        'h3_custom',
        parent=styles['h3'],
        fontSize=14,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor('#333333') # Gris oscuro
    )
    normal_style = styles['Normal']
    bullet_style = styles['Bullet']
    centered_bold = ParagraphStyle(
        'centered_bold',
        parent=normal_style,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Encabezado del informe
    story.append(Paragraph(f"Informe de SEO Local: {business_data.nombre}", h1_style))
    if business_data.direccion and business_data.direccion.direccion_completa:
        story.append(Paragraph(business_data.direccion.direccion_completa, centered_bold))
    story.append(Spacer(1, 0.2 * inch))

    # --- OPTIMIZACIÓN ---
    story.append(Paragraph("OPTIMIZACIÓN", h2_style))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>Grado de completitud del perfil:</b>", h3_style))
    completeness = business_data.perfil_completitud if business_data.perfil_completitud is not None else 0
    story.append(Paragraph(f"{completeness:.1f}%", normal_style))
    story.append(Spacer(1, 0.1 * inch))

    completeness_items = [
        ("Tiene nombre", business_data.tiene_nombre),
        ("Tiene dirección", business_data.tiene_direccion),
        ("Tiene teléfonos", business_data.tiene_telefono),
        ("Tiene página web asociada", business_data.tiene_website),
        ("Tiene categoría principal", business_data.tiene_categoria_principal),
        ("Tiene categorías secundarias", business_data.tiene_categorias_secundarias),
        ("Tiene horario", business_data.horario_normal), # Asumiendo que si tiene horario normal, está cubierto
        ("Tiene horarios especiales", business_data.horario_festivo),
        ("Tiene valoraciones", business_data.tiene_valoraciones),
        ("Tiene reseñas", business_data.n_valoraciones is not None and business_data.n_valoraciones > 0),
        ("Tiene fotos y videos", business_data.tiene_fotos),
        ("El negocio está operativo", business_data.tiene_estado_operativo)
    ]
    data = [
    ["Tiene nombre", "✅"],
    ["Tiene dirección", "✅"],
    ["Tiene teléfonos", "✅"],
    ["Tiene página web asociada", "✅"],
    ["Tiene categoría principal", "❌"],
    ["Tiene categorías secundarias", "✅"]
]

table = Table(data, colWidths=[200, 30])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#57B4BA")),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#015551")),
    ('BOX', (0, 0), (-1, -1), 0.25, colors.HexColor("#015551")),
]))



    for item_text, item_value in completeness_items:
        status_icon = "✔️" if item_value else "❌" if item_value is False else "❔"
        story.append(Paragraph(f"{status_icon} {item_text}", normal_style))
    story.append(Spacer(1, 0.2 * inch))

"""
    # --- POSICIONAMIENTO ---
    story.append(Paragraph("POSICIONAMIENTO", h2_style))
    story.append(Spacer(1, 0.1 * inch))
    positioning_text = f"El negocio {business_data.nombre} actualmente {'SÍ' if business_data.top5 else 'NO'} posiciona en el top 5 para la búsqueda <b>{business_data.palabra_busqueda}</b>." 
    story.append(Paragraph(positioning_text, normal_style))
    story.append(Spacer(1, 0.1 * inch))

    if business_data.categorias_no_incluidas:
        story.append(Paragraph("<b>Palabras clave que los competidores también usan:</b>", h3_style))
        for cat in business_data.categorias_no_incluidas:
            story.append(Paragraph(f"• {cat}", bullet_style))
        story.append(Spacer(1, 0.1 * inch))

    if business_data.palabras_clave:
        story.append(Paragraph("<b>Recomendación de palabras clave:</b>", h3_style))
        keyword_data = [["Palabra clave", "Índice de competición", "Búsquedas mensuales"]] 
        for pk in business_data.palabras_clave:
            keyword_data.append([
                pk.keyword or "N/A",
                str(pk.indice_competicion) if pk.indice_competicion is not None else "N/A",
                str(pk.busquedas_mensuales) if pk.busquedas_mensuales is not None else "N/A"
            ])
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table = Table(keyword_data)
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("<b>Algunos factores que cuentan para el posicionamiento:</b>", h3_style))
    if business_data.URL_valida_para_SEO is not None and business_data.website:
        url_status = "está optimizada" if business_data.URL_valida_para_SEO else "NO está optimizada"
        story.append(Paragraph(f"• La URL de la página web '{business_data.website}' {url_status} para el SEO.", normal_style))
    if business_data.n_fotos is not None and business_data.n_fotos_media is not None:
        photos_comparison = "MÁS" if business_data.n_fotos > business_data.n_fotos_media else "MENOS" if business_data.n_fotos < business_data.n_fotos_media else "IGUAL"
        story.append(Paragraph(f"• Tiene {business_data.n_fotos} fotos y vídeos. Es {photos_comparison} que la media, {business_data.n_fotos_media}.", normal_style)) 
    if business_data.n_valoraciones is not None and business_data.n_reviews_media is not None:
        reviews_comparison = "MÁS" if business_data.n_valoraciones > business_data.n_reviews_media else "MENOS" if business_data.n_valoraciones < business_data.n_reviews_media else "IGUAL"
        story.append(Paragraph(f"• Tiene {business_data.n_valoraciones} reseñas. Es {reviews_comparison} que la media, {business_data.n_reviews_media}.", normal_style)) 
    story.append(Spacer(1, 0.2 * inch))

    # --- REPUTACIÓN ---
    story.append(Paragraph("REPUTACIÓN", h2_style))
    story.append(Spacer(1, 0.1 * inch))
    if business_data.valoracion_media is not None:
        reputation_text = f"La puntuación media es de {business_data.valoracion_media:.1f}. Se considera una {'buena' if business_data.buena_valoracion else 'mala'} valoración." 
        story.append(Paragraph(reputation_text, normal_style))
    story.append(Spacer(1, 0.1 * inch))

    if business_data.palabras_connotacion_positiva:
        story.append(Paragraph("<b>Principales palabras que los clientes utilizan en las reseñas con una connotación positiva:</b>", h3_style))
        story.append(Paragraph(", ".join(business_data.palabras_connotacion_positiva), normal_style)) 
        story.append(Spacer(1, 0.1 * inch))

    if business_data.palabras_connotacion_negativa:
        story.append(Paragraph("<b>Principales palabras que los clientes utilizan en las reseñas con una connotación negativa:</b>", h3_style))
        story.append(Paragraph(", ".join(business_data.palabras_connotacion_negativa), normal_style)) 
        story.append(Spacer(1, 0.1 * inch))

    if business_data.sentimiento_medio is not None:
        # Asumiendo que sentimiento_medio > 0 implica positivo, < 0 negativo, = 0 neutral
        sentiment_description = "positivo" if business_data.sentimiento_medio > 0 else "negativo" if business_data.sentimiento_medio < 0 else "neutral"
        story.append(Paragraph(f"El sentimiento promedio de las reseñas es {sentiment_description}.", normal_style)) 
    if business_data.magnitud_sentimiento_media is not None:
        # Asumiendo una escala de 0 a 1 para magnitud
        intensity_description = "relativamente alta" if business_data.magnitud_sentimiento_media > 0.5 else "relativamente baja"
        story.append(Paragraph(f"La intensidad del sentimiento que presentan las reseñas se podría describir como: {intensity_description}.", normal_style)) 
    story.append(Spacer(1, 0.2 * inch))

    # --- CITACIONES LOCALES ---
    story.append(Paragraph("CITACIONES LOCALES", h2_style))
    story.append(Spacer(1, 0.1 * inch))
    if business_data.fuentes_consultadas is not None and business_data.fuentes_encontradas is not None:
        story.append(Paragraph(f"Se ha encontrado el negocio en {business_data.fuentes_encontradas} de {business_data.fuentes_consultadas} directorios locales consultados.", normal_style))
    story.append(Spacer(1, 0.1 * inch))

    if business_data.fuentes_no_encontradas:
        story.append(Paragraph("<b>Directorios locales en los que NO se ha encontrado:</b>", h3_style))
        story.append(Paragraph(", ".join(business_data.fuentes_no_encontradas), normal_style))
        story.append(Spacer(1, 0.1 * inch))

    consistency_items = [
        ("Consistencia en el nombre", business_data.consistencia_nombre),
        ("Consistencia en la ciudad", business_data.consistencia_localidad),
        ("Consistencia en la provincia", business_data.consistencia_provincia),
        ("Consistencia en la dirección", business_data.consistencia_direccion),
    ]

    story.append(Paragraph("<b>Consistencia en directorios:</b>", h3_style))
    for item_text, item_value in consistency_items:
        status_icon = "✔️" if item_value else "❌" if item_value is False else "❔"
        story.append(Paragraph(f"{status_icon} {item_text}", normal_style))

    if business_data.inconsistencias_directorios:
        story.append(Paragraph("<b>Inconsistencias detectadas en directorios:</b>", h3_style))
        story.append(Paragraph(", ".join(business_data.inconsistencias_directorios), normal_style))
    story.append(Spacer(1, 0.2 * inch))

    # --- SUGERENCIAS FINALES ---
    story.append(Paragraph("SUGERENCIAS FINALES", h2_style))
    story.append(Spacer(1, 0.1 * inch))
    suggestions = [
        "Completa cada apartado de tu perfil a la perfección. Tu perfil de Google Business Profile es tu escaparate digital más importante. Google premia los perfiles que tienen toda la información posible y bien rellenada. Esto incluye horarios normales y también los horarios especiales para festivos o eventos.", 
        "Puedes añadir las palabras clave recomendadas en las categorías principales o secundarias del perfil. Es importante que los clientes incluyan palabras clave en las reseñas, y que esas palabras clave estén en sintonía con las palabras clave trabajadas en el perfil. Puedes sugerirles amablemente que mencionen el producto o servicio específico que les gustó, o la experiencia que tuvieron.", 
        "Gestiona y responde a todas las reseñas, tanto las positivas como las negativas. Agradece las reseñas positivas y aborda las negativas de forma constructiva y profesional. Recuerda que una buena respuesta a una reseña negativa puede transformar una mala experiencia en una demostración de excelente servicio al cliente.", 
        "Mantén la información de tu negocio (Nombre, Dirección, Teléfono - NAP) exactamente igual en todas partes. La consistencia es clave para que Google confíe en que tu información es la correcta." , 
        "También puedes investigar más directorios locales que sean del interés de tu negocio para registrarlo. Algunos recomendados son: Cylex, Yelp, Foursquare y Encuentre-abierto."
    ]
    for suggestion in suggestions:
        story.append(Paragraph(f"• {suggestion}", bullet_style))
        story.append(Spacer(1, 0.1 * inch))

    story.append(Spacer(1, 0.5 * inch))

    # Construir el PDF
    doc.build(story)

# --- EJEMPLO DE USO CON DATOS DE Informe_Alcosto.pdf ---
if __name__ == "__main__":
    # Tu código principal va aquí
    sample_business = Business(
        place_id="sample_alkosto_id",
        main_business=True,
        palabra_busqueda="Textil", 
        nombre="Alkosto Carrera 30", 
        direccion=BusinessAddress(
            calle="Ave Cra 30 #10-25",
            ciudad="Bogotá",
            provincia="Cundinamarca",
            pais="Colombia",
            direccion_completa="Ave Cra 30 #10-25, Puente Aranda, Bogotá, Cundinamarca, Colombia" 
        ),
        website="https://www.alkosto.com/",
        n_fotos=10, 
        n_valoraciones=27461, 
        perfil_completitud=95.7, 
        # Atributos de completitud (basados en la imagen del PDF)
        tiene_nombre=True,
        tiene_direccion=True,
        tiene_telefono=True,
        tiene_website=True,
        tiene_fotos=True,
        tiene_valoraciones=True, # Asumido por n_valoraciones > 0
        tiene_valoracion_media=True, # Asumido por valoracion_media
        tiene_categoria_principal=True,
        tiene_categorias_secundarias=True,
        tiene_estado_operativo=True,
        horario_normal=True,
        horario_festivo=False, # Si no se menciona o es 0, asumimos False
        
        URL_valida_para_SEO=True, 
        buena_valoracion=True, # 4.4 se considera buena valoración 
        top5=False, 
        n_fotos_media=8, 
        n_reviews_media=4773, 
        categorias_no_incluidas=["Canelo Textil", "CBA TEXTIL", "Indultex", "Mayor textile SRL", "Tejidos Córdoba"], # Nombres de competidores en PDF 
        # deberia_incluir_categoria_en_nombre=False, # No hay info específica en PDF
        # palabras_clave_en_resenas=... # Podrías extraer estas del PDF si tienes un proceso para ello
        
        palabras_clave=[
            BusinessKeywordSuggestions(keyword="fabricantes textiles", indice_competicion=71, busquedas_mensuales=9900), 
            BusinessKeywordSuggestions(keyword="tienda textil", indice_competicion=45, busquedas_mensuales=1000), 
            BusinessKeywordSuggestions(keyword="gotextil", indice_competicion=59, busquedas_mensuales=390), 
            BusinessKeywordSuggestions(keyword="textil service", indice_competicion=8, busquedas_mensuales=260), 
            BusinessKeywordSuggestions(keyword="alexis textil", indice_competicion=4, busquedas_mensuales=260), 
            BusinessKeywordSuggestions(keyword="textil hosteleria", indice_competicion=32, busquedas_mensuales=140), 
            BusinessKeywordSuggestions(keyword="textil com", indice_competicion=16, busquedas_mensuales=140), 
            BusinessKeywordSuggestions(keyword="hotel textil", indice_competicion=53, busquedas_mensuales=110), 
            BusinessKeywordSuggestions(keyword="aris textil", indice_competicion=4, busquedas_mensuales=90) 
        ],
        valoracion_media=4.4, 
        palabras_connotacion_positiva=["supermercado", "precios", "articulos", "opción", "productos", "variedad", "promociones", "selección"], 
        palabras_connotacion_negativa=["productos", "tienda", "servicio", "ofertas"], 
        sentimiento_medio=0.8, # El PDF indica "positivo", esto es una representación numérica
        magnitud_sentimiento_media=0.3, # El PDF indica "relativamente baja", esto es una representación numérica
        # orden_por_sentimiento=... # No hay campo directo para esto en el Business dataclass para una lista de competidores

        fuentes_consultadas=3,
        fuentes_encontradas=0,
        fuentes_no_encontradas=["Firmania", "Habitissimo", "Paginas Amarillas"],
        # Inconsistencias (asumido como False ya que no se encontró en directorios y el PDF indica inconsistencias)
        consistencia_nombre=False, 
        consistencia_localidad=False, 
        consistencia_provincia=False, 
        consistencia_direccion=False, 
        inconsistencias_directorios=["Nombre", "Ciudad", "Provincia", "Dirección"] # Los items listados en PDF ]
    )
    print(sample_business)
    # Generar el PDF
    generate_seo_report_pdf(sample_business, "Informe_SEO_Alkosto_Dinamico.pdf")
    print("Informe PDF generado como 'Informe_SEO_Alkosto_Dinamico.pdf'")
