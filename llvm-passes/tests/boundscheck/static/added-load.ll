; CHECK: @f
define void @f() {
; CHECK: %a = alloca i32, i32 16
  %a = alloca i32, i32 16

; CHECK: %a = alloca i32*
  %b = alloca i32*

; CHECK: store i32* %a, i32** %b
  store i32* %a, i32** %b

; CHECK: %e = load i32*, i32**  %b
  %e = load i32*, i32** %b

; CHECK: call void @__coco_check_bounds({{.*}}i32 100, i32 16{{.*}})
; CHECK: %a.idx = getelementptr i32, i32* %e, i32 100
  %a.idx = getelementptr i32, i32* %e, i32 100
  store i32 1337, i32* %a.idx
  ret void
}
