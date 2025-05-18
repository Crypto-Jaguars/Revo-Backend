import { Entity, Column, PrimaryGeneratedColumn, ManyToOne, CreateDateColumn, UpdateDateColumn, DeleteDateColumn, JoinColumn } from 'typeorm';
import { Farmer } from '../../farmers/entities/farmer.entity';

@Entity('products')
export class Product {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ length: 255 })
  name: string;

  @Column({ type: 'text', nullable: true })
  description: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  price: number;

  @Column({ name: 'price_unit', length: 50 })
  priceUnit: string;

  @Column({ name: 'farmer_id' })
  farmerId: string;

  @ManyToOne(() => Farmer, farmer => farmer.products)
  @JoinColumn({ name: 'farmer_id' })
  farmer: Farmer;

  @Column({ length: 100 })
  category: string;

  @Column({ name: 'sub_category', length: 100, nullable: true })
  subCategory: string;

  @Column({ type: 'jsonb', nullable: true })
  images: string[];

  @Column({ name: 'stock_quantity', default: 0 })
  stockQuantity: number;

  @Column({ name: 'harvest_date', type: 'timestamp', nullable: true })
  harvestDate: Date;

  @Column({ type: 'jsonb', nullable: true })
  certifications: string[];

  @Column({ type: 'jsonb', nullable: true })
  seasonality: string[];

  @Column({ name: 'farming_method', length: 50, nullable: true })
  farmingMethod: string;

  @Column({ name: 'available_for_delivery', default: false })
  availableForDelivery: boolean;

  @Column({ name: 'pickup_available', default: true })
  pickupAvailable: boolean;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  @DeleteDateColumn({ name: 'deleted_at' })
  deletedAt: Date;
}