"use client";

import { useFormContext } from "react-hook-form";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { VoucherType } from "../types";
import { VoucherFormData } from "../schemas";

export const VoucherHeaderForm = () => {
  const { register, setValue, watch, formState: { errors } } = useFormContext<VoucherFormData>();
  const voucherType = watch("voucher_type");

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div className="space-y-2">
        <Label>Voucher Type</Label>
        <Select
          value={voucherType}
          onValueChange={(val) => setValue("voucher_type", val as VoucherType)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            {Object.values(VoucherType).map(type => (
              <SelectItem key={type} value={type}>{type}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.voucher_type && <p className="text-xs text-red-500">{errors.voucher_type.message}</p>}
      </div>

      <div className="space-y-2">
        <Label>Voucher Date</Label>
        <Input type="date" {...register("voucher_date")} />
        {errors.voucher_date && <p className="text-xs text-red-500">{errors.voucher_date.message}</p>}
      </div>

      <div className="space-y-2">
        <Label>Narration</Label>
        <Input placeholder="General narration..." {...register("narration")} />
      </div>
    </div>
  );
};
