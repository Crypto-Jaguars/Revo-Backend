import { MigrationInterface, QueryRunner, Table, TableIndex, TableForeignKey } from 'typeorm';

export class CreateProductTable1624536978524 implements MigrationInterface {
  name = 'CreateProductTable1624536978524';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.createTable(
      new Table({
        name: 'products',
        columns: [
          {
            name: 'id',
            type: 'uuid',
            isPrimary: true,
            generationStrategy: 'uuid',
            default: 'uuid_generate_v4()',
          },
          {
            name: 'name',
            type: 'varchar',
            length: '255',
            isNullable: false,
          },
          {
            name: 'description',
            type: 'text',
            isNullable: true,
          },
          {
            name: 'price',
            type: 'decimal',
            precision: 10,
            scale: 2,
            isNullable: false,
          },
          {
            name: 'price_unit',
            type: 'varchar',
            length: '50',
            isNullable: false,
          },
          {
            name: 'farmer_id',
            type: 'uuid',
            isNullable: false,
          },
          {
            name: 'category',
            type: 'varchar',
            length: '100',
            isNullable: false,
          },
          {
            name: 'sub_category',
            type: 'varchar',
            length: '100',
            isNullable: true,
          },
          {
            name: 'images',
            type: 'jsonb',
            isNullable: true,
          },
          {
            name: 'stock_quantity',
            type: 'integer',
            isNullable: false,
            default: 0,
          },
          {
            name: 'harvest_date',
            type: 'timestamp',
            isNullable: true,
          },
          {
            name: 'certifications',
            type: 'jsonb',
            isNullable: true,
          },
          {
            name: 'seasonality',
            type: 'jsonb',
            isNullable: true,
          },
          {
            name: 'farming_method',
            type: 'varchar',
            length: '50',
            isNullable: true,
          },
          {
            name: 'available_for_delivery',
            type: 'boolean',
            default: false,
          },
          {
            name: 'pickup_available',
            type: 'boolean',
            default: true,
          },
          {
            name: 'created_at',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
          },
          {
            name: 'updated_at',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
          },
          {
            name: 'deleted_at',
            type: 'timestamp',
            isNullable: true,
          },
        ],
      }),
      true
    );

    // Add indexes
    await queryRunner.createIndex(
      'products',
      new TableIndex({
        name: 'IDX_PRODUCTS_CATEGORY',
        columnNames: ['category'],
      })
    );

    await queryRunner.createIndex(
      'products',
      new TableIndex({
        name: 'IDX_PRODUCTS_FARMER',
        columnNames: ['farmer_id'],
      })
    );

    // Add foreign key (assuming farmers table exists)
    await queryRunner.createForeignKey(
      'products',
      new TableForeignKey({
        name: 'FK_PRODUCTS_FARMER',
        columnNames: ['farmer_id'],
        referencedTableName: 'farmers',
        referencedColumnNames: ['id'],
        onDelete: 'CASCADE',
      })
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // Remove foreign key
    await queryRunner.dropForeignKey('products', 'FK_PRODUCTS_FARMER');

    // Remove indexes
    await queryRunner.dropIndex('products', 'IDX_PRODUCTS_FARMER');
    await queryRunner.dropIndex('products', 'IDX_PRODUCTS_CATEGORY');

    // Drop table
    await queryRunner.dropTable('products');
  }
}