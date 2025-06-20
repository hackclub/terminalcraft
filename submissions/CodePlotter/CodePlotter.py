print("""
 _____           _     ______ _       _   _            
/  __ \\         | |    | ___ \\ |     | | | |           
| /  \\/ ___   __| | ___| |_/ / | ___ | |_| |_ ___ _ __ 
| |    / _ \\ / _` |/ _ \\  __/| |/ _ \\| __| __/ _ \\ '__|
| \\__/\\ (_) | (_| |  __/ |   | | (_) | |_| ||  __/ |   
 \\____/\\___/ \\__,_|\\___\\_|   |_|\\___/ \\__|\\__\\___|_|                                         

""")

import re
import math
import os
import itertools

G_TOL = 1e-6

def parse_xy(g_lns):
    segs = []
    curr_seg = []
    lx, ly = 0.0, 0.0
    in_s = False

    for idx, l in enumerate(g_lns):
        l = l.strip().upper().split(';')[0]
        if not l: continue

        pts = l.split()
        cmd = None
        xc, yc = None, None
        zp = False
        xyp = False
        g01 = False
        g92 = False

        tx, ty = lx, ly

        for p_item in pts:
            if not p_item: continue
            ch = p_item[0]
            try:
                v_str = p_item[1:]
                if ch == 'G':
                    g_v = int(float(v_str))
                    if g_v == 0 or g_v == 1:
                        cmd = f"G{g_v}"
                        g01 = True
                    elif g_v == 92:
                        g92 = True
                elif ch == 'X':
                    xc = float(v_str)
                    tx = xc
                    xyp = True
                elif ch == 'Y':
                    yc = float(v_str)
                    ty = yc
                    xyp = True
                elif ch == 'Z':
                    zp = True
            except (ValueError, IndexError):
                continue

        if g01:
            z_om = zp and not xyp
            cpx = xc if xc is not None else lx
            cpy = yc if yc is not None else ly

            cp = {'x': cpx, 'y': cpy, 'cmd': cmd, 'z_only': z_om, 'line': idx}
            mvd_xy = abs(lx - cpx) > G_TOL or abs(ly - cpy) > G_TOL

            if cmd == "G0":
                if curr_seg:
                    segs.append(list(curr_seg))
                if mvd_xy:
                    sp_g0 = {'x': lx, 'y': ly, 'cmd': "G0_START", 'z_only': False, 'line': idx}
                    g0_s = [sp_g0, cp]
                    segs.append(g0_s)
                curr_seg = []
                in_s = False

            elif cmd == "G1":
                if not in_s and mvd_xy:
                    sp_g1 = {'x': lx, 'y': ly, 'cmd': "G1", 'z_only': False, 'line': idx}
                    curr_seg.append(sp_g1)

                if mvd_xy:
                    curr_seg.append(cp)
                    in_s = True
                elif z_om and in_s:
                    segs.append(list(curr_seg))
                    curr_seg = []
                    in_s = False
            lx, ly = cpx, cpy
        elif g92:
            if in_s:
                segs.append(list(curr_seg))
                curr_seg = []
                in_s = False
            if xc is not None: lx = xc
            if yc is not None: ly = yc
        else:
            if in_s:
                segs.append(list(curr_seg))
                curr_seg = []
                in_s = False
            if xyp:
                lx, ly = tx, ty
    if curr_seg:
        segs.append(curr_seg)
    return [s for s in segs if len(s) >= 2], lx, ly

def calc_bds(segs):
    if not segs:
        return None
    mnx, mny, mxx, mxy_ = float('inf'), float('inf'), float('-inf'), float('-inf')
    hp = False
    for seg in segs:
        for pt in seg:
            hp = True
            mnx, mxx = min(mnx, pt['x']), max(mxx, pt['x'])
            mny, mxy_ = min(mny, pt['y']), max(mxy_, pt['y'])
    return {"min_x": mnx, "max_x": mxx, "min_y": mny, "max_y": mxy_} if hp else None

def gen_trans_gcode(og_lns, xs=1.0, ys=1.0, zs=1.0,
                           xo=0.0, yo=0.0, zo=0.0,
                           pxo=0.0, pyo=0.0, rot_a=0.0):
    mod_gc = []
    c_pat = re.compile(r"([XYZ])([-+]?\d*\.?\d*)")
    rot_r = math.radians(rot_a)
    ct = math.cos(rot_r)
    st = math.sin(rot_r)

    for l in og_lns:
        pts = l.split(';', 1)
        cd_pt = pts[0]
        cm_pt = f";{pts[1]}" if len(pts) > 1 else ""
        ccu = cd_pt.strip().upper()
        is_mv_cmd = ccu.startswith('G0') or ccu.startswith('G1')
        is_set_cmd = ccu.startswith('G92')

        if is_mv_cmd or is_set_cmd:
            mchs = list(c_pat.finditer(cd_pt))
            if mchs:
                ax_v = {}
                for m in mchs:
                    ax = m.group(1).upper()
                    try:
                        v = float(m.group(2))
                        ax_v[ax] = v
                    except ValueError:
                        pass
                if 'X' in ax_v and 'Y' in ax_v:
                    sx = ax_v['X'] * xs
                    sy = ax_v['Y'] * ys
                    if rot_a != 0:
                        rx = sx * ct - sy * st
                        ry = sx * st + sy * ct
                        sx, sy = rx, ry
                    fx = sx + xo - pxo
                    fy = sy + yo - pyo
                    ax_v['X'] = fx
                    ax_v['Y'] = fy
                if 'Z' in ax_v:
                    ax_v['Z'] = (ax_v['Z'] * zs) + zo
                mod_cd_pt = ccu.split()[0]
                for ax, v_val in sorted(ax_v.items()):
                    mod_cd_pt += f" {ax}{v_val:.6f}"
                mod_l = mod_cd_pt + cm_pt
            else:
                mod_l = cd_pt + cm_pt
        else:
            mod_l = cd_pt + cm_pt
        mod_gc.append(mod_l)
    return mod_gc

def crop_gcode(og_lns, bw, bh, xs=1.0, ys=1.0, zs=1.0,
                  xo=0.0, yo=0.0, zo=0.0, pxo=0.0, pyo=0.0, rot_a=0.0):
    mod_gc = []
    c_pat = re.compile(r"([XYZ])([-+]?\d*\.?\d*)")
    rot_r = math.radians(rot_a)
    ct = math.cos(rot_r)
    st = math.sin(rot_r)
    lx, ly = 0.0, 0.0

    for l in og_lns:
        pts = l.split(';', 1)
        cd_pt = pts[0]
        cm_pt = f";{pts[1]}" if len(pts) > 1 else ""
        ccu = cd_pt.strip().upper()
        is_mv_cmd = ccu.startswith('G0') or ccu.startswith('G1')

        if is_mv_cmd:
            mchs = list(c_pat.finditer(cd_pt))
            if mchs:
                ax_v = {}
                for m in mchs:
                    ax = m.group(1).upper()
                    try:
                        v = float(m.group(2))
                        ax_v[ax] = v
                    except ValueError:
                        pass
                if 'X' in ax_v and 'Y' in ax_v:
                    sx = ax_v['X'] * xs
                    sy = ax_v['Y'] * ys
                    if rot_a != 0:
                        rx = sx * ct - sy * st
                        ry = sx * st + sy * ct
                        sx, sy = rx, ry
                    fx = sx + xo - pxo
                    fy = sy + yo - pyo
                    fx_clamped = max(0, min(fx, bw))
                    fy_clamped = max(0, min(fy, bh))
                    
                    ax_v['X'] = fx_clamped
                    ax_v['Y'] = fy_clamped
                    lx, ly = fx_clamped, fy_clamped
                if 'Z' in ax_v:
                    ax_v['Z'] = (ax_v['Z'] * zs) + zo
                mod_cd_pt = ccu.split()[0]
                for ax, v_val in sorted(ax_v.items()):
                    mod_cd_pt += f" {ax}{v_val:.6f}"
                mod_l = mod_cd_pt + cm_pt
                mod_gc.append(mod_l)
            else:
                mod_gc.append(cd_pt + cm_pt)
        else:
            mod_gc.append(cd_pt + cm_pt)
    return mod_gc

def apply_trans_coords(ocs, tp):
    ts = []
    xs = tp['x_scale']
    ys = tp['y_scale']
    xo = tp['x_offset']
    yo = tp['y_offset']
    rot_a = math.radians(tp.get('rotation_angle', 0))

    for seg in ocs:
        ns = []
        for pt in seg:
            sx = pt['x'] * xs
            sy = pt['y'] * ys
            if rot_a != 0:
                ct = math.cos(rot_a)
                st = math.sin(rot_a)
                rx = sx * ct - sy * st
                ry = sx * st + sy * ct
                tx_ = rx + xo
                ty_ = ry + yo
            else:
                tx_ = sx + xo
                ty_ = sy + yo
            ns.append({**pt, 'x': tx_, 'y': ty_})
        ts.append(ns)
    return ts

def center_on_bed(segs, tp, bw, bh):
    if not segs:
        return tp
    tmp_s = apply_trans_coords(segs, {
        'x_scale': tp['x_scale'],
        'y_scale': tp['y_scale'],
        'x_offset': 0,
        'y_offset': 0,
        'rotation_angle': tp.get('rotation_angle', 0)
    })
    bds = calc_bds(tmp_s)
    if not bds:
        return tp
    pw = bds['max_x'] - bds['min_x']
    ph = bds['max_y'] - bds['min_y']
    pcx = bds['min_x'] + pw / 2.0
    pcy = bds['min_y'] + ph / 2.0
    bcx = bw / 2.0
    bcy = bh / 2.0
    nt = tp.copy()
    nt['x_offset'] = bcx - pcx
    nt['y_offset'] = bcy - pcy
    return nt

def proc_multi(fps, tfs, bw=220, bh=220, crop=False):
    mgc = []
    for i, (fp, tf) in enumerate(zip(fps, tfs)):
        try:
            with open(fp, 'r', errors='ignore') as f:
                lns = [l.strip() for l in f if l.strip()]
            if not lns:
                print(f"Skipping empty file: {os.path.basename(fp)}")
                continue
            
            if crop:
                tf_lns = crop_gcode(
                    lns, bw, bh,
                    x_scale=tf.get('x_scale', 1.0),
                    y_scale=tf.get('y_scale', 1.0),
                    z_scale=tf.get('z_scale', 1.0),
                    x_offset=tf.get('x_offset', 0.0),
                    y_offset=tf.get('y_offset', 0.0),
                    z_offset=tf.get('z_offset', 0.0),
                    pen_x_offset=tf.get('pen_x_offset', 0.0),
                    pen_y_offset=tf.get('pen_y_offset', 0.0),
                    rotation_angle=tf.get('rotation_angle', 0.0)
                )
            else:
                tf_lns = gen_trans_gcode(
                    lns,
                    x_scale=tf.get('x_scale', 1.0),
                    y_scale=tf.get('y_scale', 1.0),
                    z_scale=tf.get('z_scale', 1.0),
                    x_offset=tf.get('x_offset', 0.0),
                    y_offset=tf.get('y_offset', 0.0),
                    z_offset=tf.get('z_offset', 0.0),
                    pen_x_offset=tf.get('pen_x_offset', 0.0),
                    pen_y_offset=tf.get('pen_y_offset', 0.0),
                    rotation_angle=tf.get('rotation_angle', 0.0)
                )
            mgc.extend(tf_lns)
        except Exception as e:
            print(f"Error processing file {fp}: {e}")
            continue
    return mgc

def interactive_single():
    fp = input("Enter G-code file path: ").strip()
    if not os.path.exists(fp):
        print(f"Error: File not found at '{fp}'")
        return
    try:
        with open(fp, 'r', errors='ignore') as f:
            g_lns = [l.strip() for l in f if l.strip()]
        if not g_lns:
            print("Error: File is empty.")
            return
        
        segs, _, _ = parse_xy(g_lns)
        bds = calc_bds(segs)
        
        xs = float(input("Enter X-axis scale (default 1.0): ") or "1.0")
        ys = float(input("Enter Y-axis scale (default 1.0): ") or "1.0")
        zs = float(input("Enter Z-axis scale (default 1.0): ") or "1.0")
        rot_a = float(input("Enter rotation angle in degrees (default 0.0): ") or "0.0")
        xo = float(input("Enter X-axis offset in mm (default 0.0): ") or "0.0")
        yo = float(input("Enter Y-axis offset in mm (default 0.0): ") or "0.0")
        zo = float(input("Enter Z-axis offset in mm (default 0.0): ") or "0.0")
        pxo = float(input("Enter Pen X offset in mm (default 0.0): ") or "0.0")
        pyo = float(input("Enter Pen Y offset in mm (default 0.0): ") or "0.0")
        bw = float(input("Enter bed width in mm (default 220.0): ") or "220.0")
        bh = float(input("Enter bed height in mm (default 220.0): ") or "220.0")
        crop = input("Crop to bed boundaries? (y/N, default N): ").lower().startswith('y')
        
        if crop:
            mod_c = crop_gcode(
                g_lns, bw, bh, xs, ys, zs, xo, yo, zo, pxo, pyo, rot_a
            )
        else:
            mod_c = gen_trans_gcode(
                g_lns, xs, ys, zs, xo, yo, zo, pxo, pyo, rot_a
            )
        
        base_n = os.path.splitext(fp)[0]
        def_out = f"{base_n}_mod.gcode"
        out_p = input(f"Enter output file path (default {def_out}): ").strip() or def_out
        
        with open(out_p, 'w') as f:
            for l_item in mod_c:
                f.write(l_item + '\n')
        print(f"Transformed G-code saved to: {out_p}")
        
        new_s, _, _ = parse_xy(mod_c)
        new_b = calc_bds(new_s)
        if new_b:
            if new_b['min_x'] < 0 or new_b['min_y'] < 0 or new_b['max_x'] > bw or new_b['max_y'] > bh:
                print("WARNING: Transformed G-code may extend outside bed boundaries!")
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
    except Exception as e:
        print(f"Error during processing: {e}")

def interactive_multi():
    files = []
    tfs = []
    bw = float(input("Enter bed width for all files in mm (default 220.0): ") or "220.0")
    bh = float(input("Enter bed height for all files in mm (default 220.0): ") or "220.0")
    
    fc = 1
    while True:
        fp = input(f"Enter path for file {fc} (or leave empty to finish adding files): ").strip()
        if not fp: break
        if not os.path.exists(fp):
            print(f"Error: File not found at '{fp}'")
            continue
        try:
            with open(fp, 'r', errors='ignore') as f:
                lns = [l.strip() for l in f if l.strip()]
            if not lns:
                print("Warning: File is empty, skipping.")
                continue
            
            segs, _, _ = parse_xy(lns)
            bds = calc_bds(segs)
            files.append(fp)
            
            print(f"--- Transformations for {os.path.basename(fp)} ---")
            tf = {}
            tf['x_scale'] = float(input("X scale (default 1.0): ") or "1.0")
            tf['y_scale'] = float(input("Y scale (default 1.0): ") or "1.0")
            tf['z_scale'] = float(input("Z scale (default 1.0): ") or "1.0")
            tf['rotation_angle'] = float(input("Rotation angle degrees (default 0.0): ") or "0.0")
            tf['x_offset'] = float(input("X offset mm (default 0.0): ") or "0.0")
            tf['y_offset'] = float(input("Y offset mm (default 0.0): ") or "0.0")
            tf['z_offset'] = float(input("Z offset mm (default 0.0): ") or "0.0")
            tf['pen_x_offset'] = float(input("Pen X offset mm (default 0.0): ") or "0.0")
            tf['pen_y_offset'] = float(input("Pen Y offset mm (default 0.0): ") or "0.0")
            
            if input("Auto-center this file on bed? (y/N, default N): ").lower().startswith('y'):
                tf = center_on_bed(segs, tf, bw, bh)
                print(f"  Auto-centered: New X offset = {tf['x_offset']:.2f}, New Y offset = {tf['y_offset']:.2f}")
            
            tfs.append(tf)
            fc += 1
        except Exception as e:
            print(f"Error loading or processing file {fp}: {e}")
            continue
    
    if not files:
        print("No files were added for merging.")
        return
    
    crop = input("Crop all files to bed boundaries? (y/N, default N): ").lower().startswith('y')
    out_p = input("Enter output file path for merged G-code (default merged.gcode): ").strip() or "merged.gcode"
    
    try:
        mgc = proc_multi(files, tfs, bw, bh, crop)
        with open(out_p, 'w') as f:
            for l_item in mgc:
                f.write(l_item + '\n')
        print(f"Merged G-code saved to: {out_p}")
    except Exception as e:
        print(f"Error creating merged file: {e}")

def scale_g(g_lns, xs=1.0, ys=1.0, zs=1.0):
    mod_g = []
    for l in g_lns:
        pts = l.split()
        mod_pts = []
        for p_item in pts:
            if p_item.startswith('X') and len(p_item) > 1:
                try:
                    xv = float(p_item[1:]) * xs
                    mod_pts.append(f'X{xv:.6f}')
                except ValueError:
                    mod_pts.append(p_item)
            elif p_item.startswith('Y') and len(p_item) > 1:
                try:
                    yv = float(p_item[1:]) * ys
                    mod_pts.append(f'Y{yv:.6f}')
                except ValueError:
                    mod_pts.append(p_item)
            elif p_item.startswith('Z') and len(p_item) > 1:
                try:
                    zv = float(p_item[1:]) * zs
                    mod_pts.append(f'Z{zv:.6f}')
                except ValueError:
                    mod_pts.append(p_item)
            else:
                mod_pts.append(p_item)
        mod_g.append(' '.join(mod_pts))
    return mod_g

def offset_g(g_lns, xo=0.0, yo=0.0, zo=0.0):
    mod_g = []
    for l in g_lns:
        pts = l.split()
        mod_pts = []
        for p_item in pts:
            if p_item.startswith('X') and len(p_item) > 1:
                try:
                    xv = float(p_item[1:]) + xo
                    mod_pts.append(f'X{xv:.6f}')
                except ValueError:
                    mod_pts.append(p_item)
            elif p_item.startswith('Y') and len(p_item) > 1:
                try:
                    yv = float(p_item[1:]) + yo
                    mod_pts.append(f'Y{yv:.6f}')
                except ValueError:
                    mod_pts.append(p_item)
            elif p_item.startswith('Z') and len(p_item) > 1:
                try:
                    zv = float(p_item[1:]) + zo
                    mod_pts.append(f'Z{zv:.6f}')
                except ValueError:
                    mod_pts.append(p_item)
            else:
                mod_pts.append(p_item)
        mod_g.append(' '.join(mod_pts))
    return mod_g

if __name__ == "__main__":
    print("G-Code Manipulation Tool")
    print("Available modes:")
    print("1. Single file transformation")
    print("2. Multi-file merge and transform")
    print("3. Legacy mode (simple scale/offset)")
    
    try:
        chc = input("Enter your choice (1-3): ").strip()
        if chc == "1":
            interactive_single()
        elif chc == "2":
            interactive_multi()
        elif chc == "3":
            fp = input("Enter path to G-code file: ")
            with open(fp, 'r') as f:
                g_lns = [l.strip() for l in f]

            xs = float(input("Enter X-axis scale factor: "))
            ys = float(input("Enter Y-axis scale factor: "))
            zs = float(input("Enter Z-axis scale factor: "))
            s_code = scale_g(g_lns, xs, ys, zs)

            xo = float(input("Enter X-axis offset: "))
            yo = float(input("Enter Y-axis offset: "))
            zo = float(input("Enter Z-axis offset: "))
            mod_c = offset_g(s_code, xo, yo, zo)

            out_fp = input("Enter path to save modified G-code: ")
            with open(out_fp, 'w') as of:
                for l_item in mod_c:
                    of.write(l_item + '\n')
            print(f"Modified G-code saved to: {out_fp}")
        else:
            print("Invalid choice. Please run again.")
    except FileNotFoundError:
        print(f"Error: Input file not found.")
    except ValueError:
        print("Error: Invalid numeric input.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
