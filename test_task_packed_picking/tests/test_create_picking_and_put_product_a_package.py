from odoo.tests import common


class TestCreatePickingAndPutProductPackage(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.wizard = self.env["test.task.packed.picking.wizard"]
        self.stock_picking = self.env["stock.picking"]
        self.stock_move = self.env["stock.move"]
        self.stock_location = self.env["stock.location"]
        self.stock_picking_type = self.env["stock.picking.type"]
        self.stock_picking_type_pack = self.env.ref("stock.picking_type_internal")
        self.stock_picking_type_pack.pack_operation_ids.unlink()
        self.stock_picking_type_pack.write(
            {
                "code": "internal",
                "name": "Internal",
                "sequence_code": "INT",
                "default_location_src_id": self.stock_location.create(
                    {"name": "Stock", "usage": "internal"}
                ).id,
                "default_location_dest_id": self.stock_location.create(
                    {"name": "Customers", "usage": "customer"}
                ).id,
            }
        )
        self.product = self.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        self.product2 = self.env["product.product"].create(
            {"name": "Product2", "type": "product"}
        )
        self.product3 = self.env["product.product"].create(
            {"name": "Product3", "type": "product"}
        )
        self.line_ids = (
            [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "qty_done": 1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.product2.id,
                        "qty_done": 1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.product3.id,
                        "qty_done": 1,
                        "serial": "1234567890",
                    },
                ),
            ],
        )

    def test_create_picking_and_put_product_a_package(self):
        wizard = self.wizard.create(
            {
                "operation_type_id": self.stock_picking_type_pack.id,
                "line_ids": self.line_ids,
            }
        )
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].product_id, self.product)
        self.assertEqual(wizard.line_ids[1].product_id, self.product2)
        self.assertEqual(wizard.line_ids[2].product_id, self.product3)
        self.assertEqual(wizard.line_ids[0].qty_done, 1)
        self.assertEqual(wizard.line_ids[1].qty_done, 1)
        self.assertEqual(wizard.line_ids[2].qty_done, 1)
        self.assertEqual(wizard.line_ids[0].serial, False)
        self.assertEqual(wizard.line_ids[1].serial, False)
        self.assertEqual(wizard.line_ids[2].serial, "1234567890")
        picking = wizard.action_create_picking()
        self.assertEqual(picking.picking_type_id, self.stock_picking_type_pack)
        self.assertEqual(
            picking.location_id, self.stock_picking_type_pack.default_location_src_id
        )
        self.assertEqual(
            picking.location_dest_id,
            self.stock_picking_type_pack.default_location_dest_id,
        )
        self.assertEqual(picking.owner_id, self.env.user.partner_id)
        self.assertEqual(len(picking.move_line_ids), 3)

    def test_create_picking_and_put_product_a_package_with_params(self):
        wizard = self.wizard.create(
            {
                "operation_type_id": self.stock_picking_type_pack.id,
                "package_name": "Package",
                "owner_id": self.env.user.partner_id.id,
                "create_lots": True,
                "set_ready": True,
                "line_ids": self.line_ids,
            }
        )
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].product_id, self.product)
        self.assertEqual(wizard.line_ids[1].product_id, self.product2)
        self.assertEqual(wizard.line_ids[2].product_id, self.product3)
        self.assertEqual(wizard.line_ids[0].qty_done, 1)
        self.assertEqual(wizard.line_ids[1].qty_done, 1)
        self.assertEqual(wizard.line_ids[2].qty_done, 1)
        self.assertEqual(wizard.line_ids[0].serial, False)
        self.assertEqual(wizard.line_ids[1].serial, False)
        self.assertEqual(wizard.line_ids[2].serial, "1234567890")
        picking = wizard.action_create_picking()
        self.assertEqual(picking.picking_type_id, self.stock_picking_type_pack)
        self.assertEqual(
            picking.location_id, self.stock_picking_type_pack.default_location_src_id
        )
        self.assertEqual(
            picking.location_dest_id,
            self.stock_picking_type_pack.default_location_dest_id,
        )
        self.assertEqual(picking.owner_id, self.env.user.partner_id)
        self.assertEqual(len(picking.move_line_ids), 3)
        self.assertEqual(picking.package_level_ids.name, "Package")
        self.assertEqual(len(picking.package_level_ids.move_line_ids), 3)
        self.assertEqual(
            picking.package_level_ids.move_line_ids[0].product_id, self.product
        )
        self.assertEqual(
            picking.package_level_ids.move_line_ids[1].product_id, self.product2
        )
        self.assertEqual(
            picking.package_level_ids.move_line_ids[2].product_id, self.product3
        )
