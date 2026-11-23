"""Interfaz web en NiceGUI conectada a las reglas de negocio y SQLModel."""

from nicegui import ui
from sqlmodel import Session

from modelos_y_reglas import crear_engine_sqlite, listar_pedidos, registrar_pedido

engine = crear_engine_sqlite()


@ui.page("/")
def pagina_principal():
    with ui.column().classes("w-full max-w-4xl mx-auto p-6 gap-4"):
        ui.label("Gestión de Pedidos — Laboratorio UAT (NiceGUI + SQLModel)").classes(
            "text-2xl font-bold text-slate-800"
        )
        ui.label(
            "Reglas activas: 10% de descuento en 5 o más unidades | "
            "Envío gratis en compras >= $50.00 (caso contrario $5.00)."
        ).classes("text-sm text-slate-600")

        with ui.card().classes("w-full p-4"):
            ui.label("Nuevo Pedido").classes("text-lg font-semibold mb-2")
            with ui.row().classes("w-full items-end gap-4"):
                cliente_input = ui.input(
                    label="Nombre del cliente",
                    placeholder="Ej. Ana López",
                ).classes("flex-1")
                cantidad_input = ui.number(
                    label="Cantidad",
                    value=1,
                    min=0,
                    step=1,
                ).classes("w-32")
                precio_input = ui.number(
                    label="Precio unitario ($)",
                    value=10.0,
                    min=0.0,
                    step=0.5,
                ).classes("w-40")

            @ui.refreshable
            def tabla_pedidos():
                with Session(engine) as session:
                    pedidos = listar_pedidos(session)

                filas = [
                    {
                        "id": p.id,
                        "cliente": p.cliente,
                        "cantidad": p.cantidad,
                        "precio": f"${p.precio_unitario:.2f}",
                        "descuento": f"${p.descuento_aplicado:.2f}",
                        "envio": "Gratis" if p.envio == 0 else f"${p.envio:.2f}",
                        "total": f"${p.total:.2f}",
                    }
                    for p in pedidos
                ]

                ui.table(
                    columns=[
                        {"name": "id", "label": "ID", "field": "id", "align": "left"},
                        {"name": "cliente", "label": "Cliente", "field": "cliente", "align": "left"},
                        {"name": "cantidad", "label": "Cant.", "field": "cantidad", "align": "right"},
                        {"name": "precio", "label": "Precio Unit.", "field": "precio", "align": "right"},
                        {"name": "descuento", "label": "Descuento", "field": "descuento", "align": "right"},
                        {"name": "envio", "label": "Envío", "field": "envio", "align": "right"},
                        {"name": "total", "label": "Total Final", "field": "total", "align": "right"},
                    ],
                    rows=filas,
                    row_key="id",
                ).classes("w-full")

            def al_guardar():
                with Session(engine) as session:
                    ok, mensaje, _ = registrar_pedido(
                        session=session,
                        cliente=cliente_input.value or "",
                        cantidad=int(cantidad_input.value or 0),
                        precio_unitario=float(precio_input.value or 0.0),
                    )
                if ok:
                    ui.notify(mensaje, type="positive")
                    cliente_input.value = ""
                    cantidad_input.value = 1
                    tabla_pedidos.refresh()
                else:
                    ui.notify(mensaje, type="warning")

            ui.button("Registrar pedido", on_click=al_guardar, icon="add_shopping_cart").classes(
                "mt-3 bg-blue-700 text-white"
            )

        ui.separator()
        ui.label("Pedidos Registrados").classes("text-lg font-semibold text-slate-700")
        tabla_pedidos()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Laboratorio UAT - NiceGUI + SQLModel", port=8080, reload=False)
