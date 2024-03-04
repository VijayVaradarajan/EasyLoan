import { Spin } from 'antd';
import { useEffect, useRef } from 'react';
import {
  AreaHighlight,
  Highlight,
  IHighlight,
  PdfHighlighter,
  PdfLoader,
  Popup,
} from 'react-pdf-highlighter';
import { useGetChunkHighlights } from '../../hooks';
import { useGetDocumentUrl } from './hooks';

import styles from './index.less';

interface IProps {
  selectedChunkId: string;
}

const HighlightPopup = ({
  comment,
}: {
  comment: { text: string; emoji: string };
}) =>
  comment.text ? (
    <div className="Highlight__popup">
      {comment.emoji} {comment.text}
    </div>
  ) : null;

const Preview = ({ selectedChunkId }: IProps) => {
  const url = useGetDocumentUrl();
  const state = useGetChunkHighlights(selectedChunkId);
  const ref = useRef<(highlight: IHighlight) => void>(() => {});

  const resetHash = () => {};

  useEffect(() => {
    if (state.length > 0) {
      ref.current(state[0]);
    }
  }, [state]);

  return (
    <div className={styles.documentContainer}>
      <PdfLoader url={url} beforeLoad={<Spin />}>
        {(pdfDocument) => (
          <PdfHighlighter
            pdfDocument={pdfDocument}
            enableAreaSelection={(event) => event.altKey}
            onScrollChange={resetHash}
            scrollRef={(scrollTo) => {
              ref.current = scrollTo;
            }}
            onSelectionFinished={() => null}
            highlightTransform={(
              highlight,
              index,
              setTip,
              hideTip,
              viewportToScaled,
              screenshot,
              isScrolledTo,
            ) => {
              const isTextHighlight = !Boolean(
                highlight.content && highlight.content.image,
              );

              const component = isTextHighlight ? (
                <Highlight
                  isScrolledTo={isScrolledTo}
                  position={highlight.position}
                  comment={highlight.comment}
                />
              ) : (
                <AreaHighlight
                  isScrolledTo={isScrolledTo}
                  highlight={highlight}
                  onChange={() => {}}
                />
              );

              return (
                <Popup
                  popupContent={<HighlightPopup {...highlight} />}
                  onMouseOver={(popupContent) =>
                    setTip(highlight, () => popupContent)
                  }
                  onMouseOut={hideTip}
                  key={index}
                >
                  {component}
                </Popup>
              );
            }}
            highlights={state}
          />
        )}
      </PdfLoader>
    </div>
  );
};

export default Preview;
