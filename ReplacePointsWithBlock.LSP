(defun c:RPWB (/ *error* _blocks lst block ss space)
  ;; Replace Points With Block
  ;; Alan J. Thompson, 08.23.11
  ;; Required subroutine: AT:ListSelect

  (vl-load-com)

  (defun *error* (msg)
    (and *AcadDoc* (vla-endundomark *AcadDoc*))
    (if (and msg (not (wcmatch (strcase msg) "*BREAK*,*CANCEL*,*QUIT*,")))
      (princ (strcat "\nError: " msg))
    )
  )

  (defun _blocks (doc / l)
    (vlax-for x (vla-get-blocks doc)
      (if (not (wcmatch (vla-get-name x) "*|*,`**"))
        (setq l (cons (vla-get-name x) l))
      )
    )
    (vl-sort l '<)
  )

  (vla-startundomark
    (cond (*AcadDoc*)
          ((setq *AcadDoc* (vla-get-activedocument (vlax-get-acad-object))))
    )
  )

  (cond ((not (setq lst (_blocks *AcadDoc*))) (alert "Zero blocks in active drawing!"))
        ((and (setq block (car (AT:ListSelect "Select block to insert:" "" 10 10 "false" lst)))
              (princ "\nSelect POINT objects to replace: ")
              (ssget "_:L" '((0 . "POINT")))
         )

         (setq space (vlax-get-property
                       *AcadDoc*
                       (if (eq (getvar 'CVPORT) 1)
                         'PaperSpace
                         'ModelSpace
                       )
                     )
         )

         (vlax-for x (setq ss (vla-get-activeselectionset *AcadDoc*))
           (if (vla-insertblock space (vla-get-coordinates x) block 1. 1. 1. 0.)
             (vla-delete x)
           )
         )

         (vla-delete ss)
        )
  )
  (*error* nil)
  (princ)
)




(defun AT:ListSelect (title label height width multi lst / fn fo d item f)
  ;; List Select Dialog (Temp DCL list box selection, based on provided list)
  ;; title - list box title
  ;; label - label for list box
  ;; height - height of box
  ;; width - width of box
  ;; multi - selection method ["true": multiple, "false": single]
  ;; lst - list of strings to place in list box
  ;; Alan J. Thompson, 09.23.08 / 05.17.10 (rewrite)
  (setq fo (open (setq fn (vl-filename-mktemp "" "" ".dcl")) "w"))
  (foreach x (list (strcat "list_select : dialog { label = \"" title "\"; spacer;")
                   (strcat ": list_box { label = \"" label "\";" "key = \"lst\";")
                   (strcat "allow_accept = true; height = " (vl-princ-to-string height) ";")
                   (strcat "width = " (vl-princ-to-string width) ";")
                   (strcat "multiple_select = " multi "; } spacer; ok_cancel; }")
             )
    (write-line x fo)
  )
  (close fo)
  (new_dialog "list_select" (setq d (load_dialog fn)))
  (start_list "lst")
  (mapcar (function add_list) lst)
  (end_list)
  (setq item (set_tile "lst" "0"))
  (action_tile "lst" "(setq item $value)")
  (setq f (start_dialog))
  (unload_dialog d)
  (vl-file-delete fn)
  (if (= f 1)
    ((lambda (s / i s l)
       (while (setq i (vl-string-search " " s))
         (setq l (cons (nth (atoi (substr s 1 i)) lst) l))
         (setq s (substr s (+ 2 i)))
       )
       (reverse (cons (nth (atoi s) lst) l))
     )
      item
    )
  )
)