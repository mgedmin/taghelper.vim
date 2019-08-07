function taghelper#curtag()
  if exists("w:TagHelperCurTag")
    return w:TagHelperCurTag
  else
    return ""
  endif
endfunction

function taghelper#cursormoved()
  if !exists('b:current_syntax') || b:current_syntax !~ '^\(c\|cpp\|python\)\(\.\|$\)'
    let w:TagHelperCurTag = ''
    return
  endif
  let w:TagHelperCurTag = pyxeval('taghelper.findtag()')
endfunction

function taghelper#bufdeleted()
  let w:TagHelperCurTag = ""
  exec 'pyx taghelper.deltags(' . expand("<abuf>") . ')'
endfunction

function taghelper#showtags()
  if !has("python") && !has("python3")
    echoerr "taghelper.vim needs Python support"
    return
  endif
  exec 'pyx taghelper.showtags(' . bufnr("") . ', ' . b:changedtick . ')'
endfunction
