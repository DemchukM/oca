from odoo.tests import Form, common, tagged


@tagged("nice")
class TestCreatePickingAndPutProductPackage(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard = cls.env["test.task.packed.picking.wizard"]
        cls.stock_picking = cls.env["stock.picking"]
        cls.stock_move = cls.env["stock.move"]
        cls.stock_location = cls.env["stock.location"]
        cls.stock_picking_type = cls.env["stock.picking.type"]
        cls.stock_picking_type_pack = cls.env.ref("stock.picking_type_internal")
        cls.stock_picking_type_pack.write(
            {
                "code": "internal",
                "name": "Internal",
                "sequence_code": "INT",
                "default_location_src_id": cls.stock_location.create(
                    {"name": "Stock", "usage": "internal"}
                ).id,
                "default_location_dest_id": cls.stock_location.create(
                    {"name": "Customers", "usage": "customer"}
                ).id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "sale_line_warn": "warning",
                "sale_line_warn_msg": "Highly corrosive",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product2",
                "sale_line_warn": "warning",
                "sale_line_warn_msg": "Highly corrosive",
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Test Product3",
                "sale_line_warn": "warning",
                "sale_line_warn_msg": "Highly corrosive",
            }
        )
        cls.line_ids = [
            {
                "product_id": cls.product,
                "qty_done": 1,
            },
            {
                "product_id": cls.product2,
                "qty_done": 1,
            },
            {
                "product_id": cls.product3,
                "qty_done": 1,
                "serial": "1234567890",
            },
        ]

    def test_create_picking_and_put_product_a_package(self):
        with Form(self.wizard) as wizard:
            wizard.operation_type_id = self.stock_picking_type_pack
            for line in self.line_ids:
                with wizard.line_ids.new() as line_wizard:
                    line_wizard.product_id = line.get("product_id")
                    line_wizard.qty_done = line.get("qty_done")
                    line_wizard.serial = line.get("serial")
            with wizard.line_ids.edit(0) as line_wizard:
                self.assertEqual(line_wizard.qty_done, 1)
                self.assertEqual(line_wizard.product_id, self.product)
                self.assertEqual(line_wizard.serial, None)
            with wizard.line_ids.edit(1) as line_wizard:
                self.assertEqual(line_wizard.qty_done, 1)
                self.assertEqual(line_wizard.product_id, self.product2)
                self.assertEqual(line_wizard.serial, None)
            with wizard.line_ids.edit(2) as line_wizard:
                self.assertEqual(line_wizard.qty_done, 1)
                self.assertEqual(line_wizard.product_id, self.product3)
                self.assertEqual(line_wizard.serial, "1234567890")
        wizard = self.wizard.create(
            {
                "operation_type_id": self.stock_picking_type_pack.id,
                "line_ids": [
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
            }
        )
        action_data = wizard.action_create_picking()
        picking = self.stock_picking.browse(action_data["res_id"])
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
        with Form(self.wizard) as wizard:
            wizard.operation_type_id = self.stock_picking_type_pack
            wizard.package_name = "Package"
            wizard.owner_id = self.env.user.partner_id
            wizard.create_lots = True
            wizard.set_ready = True
            for line in self.line_ids:
                with wizard.line_ids.new() as line_wizard:
                    line_wizard.product_id = line.get("product_id")
                    line_wizard.qty_done = line.get("qty_done")
                    line_wizard.serial = line.get("serial")
            self.assertEqual(len(wizard.line_ids), 3)
            with wizard.line_ids.edit(0) as line_wizard:
                self.assertEqual(line_wizard.qty_done, 1)
                self.assertEqual(line_wizard.product_id, self.product)
                self.assertEqual(line_wizard.serial, None)
            with wizard.line_ids.edit(1) as line_wizard:
                self.assertEqual(line_wizard.qty_done, 1)
                self.assertEqual(line_wizard.product_id, self.product2)
                self.assertEqual(line_wizard.serial, None)
            with wizard.line_ids.edit(2) as line_wizard:
                self.assertEqual(line_wizard.qty_done, 1)
                self.assertEqual(line_wizard.product_id, self.product3)
                self.assertEqual(line_wizard.serial, "1234567890")
        wizard = self.wizard.create(
            {
                "operation_type_id": self.stock_picking_type_pack.id,
                "package_name": "Package",
                "owner_id": self.env.user.partner_id.id,
                "create_lots": True,
                "set_ready": True,
                "line_ids": [
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
            }
        )
        action_data = wizard.action_create_picking()
        picking = self.stock_picking.browse(action_data["res_id"])
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
        self.assertEqual(picking.package_level_ids[0].package_id.name, "Package")
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
