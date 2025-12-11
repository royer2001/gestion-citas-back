"""
Servicio para generación de PDFs de citas médicas.
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFService:
    """Servicio para generación de documentos PDF."""
    
    @staticmethod
    def generar_pdf_citas_confirmadas(fecha: str, area: dict, citas: list) -> BytesIO:
        """
        Genera un PDF con la lista de citas confirmadas para impresión.
        Las citas se separan por turno (Mañana y Tarde).
        
        Args:
            fecha: Fecha de las citas (YYYY-MM-DD)
            area: Diccionario con id y nombre del área
            citas: Lista de citas con datos del paciente y horario
            
        Returns:
            BytesIO: Buffer con el contenido del PDF
        """
        buffer = BytesIO()
        
        # Configurar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=6*mm,
            textColor=colors.HexColor('#1a365d'),
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulo
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=4*mm,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica'
        )
        
        # Estilo para información adicional
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=3*mm,
            textColor=colors.HexColor('#4a5568')
        )
        
        # Estilo para el pie de página
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718096')
        )
        
        # Estilo para encabezado de turno - Mañana
        turno_manana_style = ParagraphStyle(
            'TurnoMananaStyle',
            parent=styles['Heading3'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceBefore=8*mm,
            spaceAfter=4*mm,
            textColor=colors.HexColor('#b45309'),  # Amber-700
            fontName='Helvetica-Bold'
        )
        
        # Estilo para encabezado de turno - Tarde
        turno_tarde_style = ParagraphStyle(
            'TurnoTardeStyle',
            parent=styles['Heading3'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceBefore=8*mm,
            spaceAfter=4*mm,
            textColor=colors.HexColor('#4338ca'),  # Indigo-700
            fontName='Helvetica-Bold'
        )
        
        # Elementos del documento
        elements = []
        
        # Título principal
        elements.append(Paragraph("CENTRO DE SALUD", title_style))
        elements.append(Paragraph("Lista de Citas Confirmadas", subtitle_style))
        elements.append(Spacer(1, 3*mm))
        
        # Formatear fecha para mostrar
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d de %B de %Y")
            # Traducir meses al español
            meses = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
            for en, es in meses.items():
                fecha_formateada = fecha_formateada.replace(en, es)
        except:
            fecha_formateada = fecha
        
        # Información del área y fecha
        elements.append(Paragraph(f"<b>Área:</b> {area.get('nombre', 'No especificada')}", info_style))
        elements.append(Paragraph(f"<b>Fecha:</b> {fecha_formateada}", info_style))
        elements.append(Paragraph(f"<b>Total de citas:</b> {len(citas)}", info_style))
        
        # Separar citas por turno
        citas_manana = []
        citas_tarde = []
        citas_sin_turno = []
        
        for cita in citas:
            horario = cita.get('horario', {}) or {}
            turno = horario.get('turno', '')
            
            if turno == 'M':
                citas_manana.append(cita)
            elif turno == 'T':
                citas_tarde.append(cita)
            else:
                citas_sin_turno.append(cita)
        
        # Función auxiliar para crear tabla de citas
        def crear_tabla_citas(citas_turno, color_header):
            if not citas_turno:
                return None
            
            # Encabezados de la tabla
            table_data = [
                ['N°', 'DNI', 'Paciente', 'Hora']
            ]
            
            # Agregar filas de citas con numeración local por turno
            for idx, cita in enumerate(citas_turno, start=1):
                paciente = cita.get('paciente', {}) or {}
                horario = cita.get('horario', {}) or {}
                
                # Nombre completo del paciente
                nombre_completo = f"{paciente.get('apellido_paterno', '')} {paciente.get('apellido_materno', '')}, {paciente.get('nombres', '')}"
                nombre_completo = nombre_completo.strip().strip(',').strip()
                if not nombre_completo:
                    nombre_completo = "No registrado"
                
                # Horario formateado
                hora_inicio = horario.get('hora_inicio', '')
                hora_fin = horario.get('hora_fin', '')
                if hora_inicio and hora_fin:
                    # Formatear hora (remover segundos si existen)
                    hora_inicio = hora_inicio[:5] if len(hora_inicio) > 5 else hora_inicio
                    hora_fin = hora_fin[:5] if len(hora_fin) > 5 else hora_fin
                    horario_str = f"{hora_inicio} - {hora_fin}"
                else:
                    horario_str = "-"
                
                table_data.append([
                    str(idx),  # Numeración local por turno
                    paciente.get('dni', 'N/A'),
                    nombre_completo,
                    horario_str
                ])
            
            # Crear tabla con anchos de columna específicos
            col_widths = [1.2*cm, 2.5*cm, 10*cm, 3*cm]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Estilo de la tabla
            table_style = TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), color_header),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Cuerpo de la tabla
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Número centrado
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # DNI centrado
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Nombre a la izquierda
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Hora centrado
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                ('BOX', (0, 0), (-1, -1), 1, color_header),
                
                # Colores alternados para filas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ])
            
            table.setStyle(table_style)
            return table
        
        # Agregar sección de Turno Mañana
        if citas_manana:
            elements.append(Paragraph(f"☀️ TURNO MAÑANA (07:30 - 13:30) — {len(citas_manana)} citas", turno_manana_style))
            tabla_manana = crear_tabla_citas(citas_manana, colors.HexColor('#d97706'))  # Amber-600
            if tabla_manana:
                elements.append(tabla_manana)
        
        # Agregar sección de Turno Tarde
        if citas_tarde:
            elements.append(Paragraph(f"🌙 TURNO TARDE (13:30 - 19:30) — {len(citas_tarde)} citas", turno_tarde_style))
            tabla_tarde = crear_tabla_citas(citas_tarde, colors.HexColor('#4f46e5'))  # Indigo-600
            if tabla_tarde:
                elements.append(tabla_tarde)
        
        # Si hay citas sin turno definido
        if citas_sin_turno:
            sin_turno_style = ParagraphStyle(
                'SinTurnoStyle',
                parent=styles['Heading3'],
                fontSize=12,
                alignment=TA_LEFT,
                spaceBefore=8*mm,
                spaceAfter=4*mm,
                textColor=colors.HexColor('#6b7280'),
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph(f"📋 SIN TURNO ASIGNADO — {len(citas_sin_turno)} citas", sin_turno_style))
            tabla_sin_turno = crear_tabla_citas(citas_sin_turno, colors.HexColor('#6b7280'))  # Gray-500
            if tabla_sin_turno:
                elements.append(tabla_sin_turno)
        
        # Si no hay citas en ningún turno
        if not citas_manana and not citas_tarde and not citas_sin_turno:
            no_data_style = ParagraphStyle(
                'NoDataStyle',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#718096'),
                spaceBefore=20*mm
            )
            elements.append(Paragraph("No hay citas confirmadas para esta fecha y área.", no_data_style))
        
        # Espacio antes del pie de página
        elements.append(Spacer(1, 10*mm))
        
        # Resumen por turnos
        if citas_manana or citas_tarde:
            resumen_style = ParagraphStyle(
                'ResumenStyle',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#4a5568'),
                spaceBefore=5*mm,
                spaceAfter=5*mm
            )
            resumen_text = []
            if citas_manana:
                resumen_text.append(f"Mañana: {len(citas_manana)}")
            if citas_tarde:
                resumen_text.append(f"Tarde: {len(citas_tarde)}")
            elements.append(Paragraph(f"<b>Resumen:</b> {' | '.join(resumen_text)} | <b>Total: {len(citas)}</b>", resumen_style))
        
        # Pie de página con fecha de generación
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"Documento generado el {fecha_generacion}", footer_style))
        elements.append(Paragraph("Este documento es válido únicamente para la fecha indicada.", footer_style))
        
        # Construir PDF
        doc.build(elements)
        
        # Regresar el buffer al inicio
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def generar_nombre_archivo(fecha: str, area_nombre: str) -> str:
        """
        Genera un nombre de archivo descriptivo para el PDF.
        
        Args:
            fecha: Fecha de las citas (YYYY-MM-DD)
            area_nombre: Nombre del área
            
        Returns:
            str: Nombre del archivo sin extensión
        """
        # Limpiar nombre del área para usar en filename
        area_limpia = area_nombre.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        return f"citas_confirmadas_{area_limpia}_{fecha}"
